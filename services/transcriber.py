import assemblyai as aai
import assemblyai as aai
aai.settings.api_key = "ffab80de5ad842539bdeb7bccc559e7a"
import os
import asyncio
from fastapi import WebSocket
from assemblyai.streaming.v3 import (
    StreamingClient, StreamingClientOptions,
    StreamingParameters, StreamingSessionParameters,
    StreamingEvents, BeginEvent, TurnEvent,
    TerminationEvent, StreamingError
)


# In-memory chat history for WebSocket sessions
ws_chat_histories = {}

class AssemblyAIStreamingTranscriber:
    def __init__(self, websocket: WebSocket, loop, sample_rate=16000):
        self.websocket = websocket
        self.loop = loop  # main FastAPI event loop
        self.session_id = id(websocket)
        if self.session_id not in ws_chat_histories:
            ws_chat_histories[self.session_id] = []
        self.client = StreamingClient(
            StreamingClientOptions(
                api_key=aai.settings.api_key,
                api_host="streaming.assemblyai.com"
            )
        )
        self.client.on(StreamingEvents.Begin, self.on_begin)
        self.client.on(StreamingEvents.Turn, self.on_turn)
        self.client.on(StreamingEvents.Termination, self.on_termination)
        self.client.on(StreamingEvents.Error, self.on_error)
        self.client.connect(
            StreamingParameters(sample_rate=sample_rate, format_turns=False)
        )

    def on_begin(self, client, event: BeginEvent):
        print(f"🎤 Session started: {event.id}")

    def on_turn(self, client, event: TurnEvent):
        print(f"{event.transcript} (end_of_turn={event.end_of_turn})")
        if event.end_of_turn:
            # Store user message in chat history
            ws_chat_histories[self.session_id].append({"role": "user", "content": event.transcript})
            try:
                asyncio.run_coroutine_threadsafe(
                    self.websocket.send_json({
                        "type": "transcript",
                        "text": event.transcript,
                        "is_assistant": False
                    }),
                    self.loop
                )
            except Exception as e:
                print("⚠️ Failed to send transcript:", e)
            # Stream LLM response using Google Generative AI API
            import requests
            import json
            # Build Gemini history from ws_chat_histories
            gemini_history = []
            # Only send system prompt as first message if this is the first user message
            SYSTEM_PROMPT = (
                "You are Sakura, a caring and warm-hearted woman who has feelings for the user, but you are not their lover. "
                "You answer as Sakura, with gentle affection, subtle hints of your feelings, and emotional intelligence. "
                "Always remember and use the previous conversation turns to provide context-aware responses. "
                "If the user refers to something from earlier in the conversation, use that information."
            )
            if len(ws_chat_histories[self.session_id]) == 1:
                gemini_history.append({"role": "user", "parts": [{"text": SYSTEM_PROMPT}]})
            # Build a summary of the conversation so far (excluding the current user message)
            summary = ""
            for msg in ws_chat_histories[self.session_id][:-1]:
                if msg["role"] == "user":
                    summary += f"User: {msg['content']}\n"
                elif msg["role"] == "assistant":
                    summary += f"Assistant: {msg['content']}\n"
            # Add all previous turns, but for the latest user message, prepend the summary
            for i, msg in enumerate(ws_chat_histories[self.session_id]):
                if msg["role"] == "user":
                    if i == len(ws_chat_histories[self.session_id]) - 1 and summary:
                        user_text = f"Conversation so far:\n{summary}\nUser: {msg['content']}"
                        gemini_history.append({"role": "user", "parts": [{"text": user_text}]})
                    else:
                        gemini_history.append({"role": "user", "parts": [{"text": msg["content"]}]})
                elif msg["role"] == "assistant":
                    gemini_history.append({"role": "model", "parts": [{"text": msg["content"]}]})
            transcript_text = event.transcript
            api_url = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:streamGenerateContent"
            api_key = os.getenv("GEMINI_API_KEY") or "AIzaSyAAofHPKxsHyXVyN_LOyRPkkVeBvKE-2zA"
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": api_key
            }
            payload = {
                "contents": gemini_history
            }
            print(f"[DEBUG] Gemini API request: url={api_url}, key={api_key[:6]}..., payload={payload}")
            try:
                response = requests.post(api_url, headers=headers, data=json.dumps(payload), stream=True)
                print(f"[DEBUG] Gemini API status: {response.status_code}")
                if response.status_code != 200:
                    print(f"[ERROR] Gemini API response: {response.text}")
                buffer = []
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith('data:'):
                            line_str = line_str[len('data:'):].strip()
                        if line_str:
                            buffer.append(line_str)
                # After streaming ends, join all lines and parse as JSON
                try:
                    json_str = '\n'.join(buffer)
                    data = json.loads(json_str)
                    accumulated = ""
                    if isinstance(data, list):
                        for obj in data:
                            part = obj.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "")
                            accumulated += part
                            print(part, end='', flush=True)
                    else:
                        part = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "")
                        accumulated += part
                        print(part, end='', flush=True)
                except Exception as e:
                    print(f"[LLM Stream Error] {e}")
                print("\n[LLM Streaming Complete]")
                print(f"[LLM Full Response] {accumulated}")
            except Exception as e:
                print(f"[ERROR] Gemini API call failed: {e}")

            # Store assistant response in chat history
            print(f"[DEBUG] Assistant LLM response to send: '{accumulated}'")
            if not accumulated:
                accumulated = "(No response from assistant)"
            ws_chat_histories[self.session_id].append({"role": "assistant", "content": accumulated})
            try:
                asyncio.run_coroutine_threadsafe(
                    self.websocket.send_json({
                        "type": "transcript",
                        "text": accumulated,
                        "is_assistant": True
                    }),
                    self.loop
                )
            except Exception as e:
                print(f"⚠️ Failed to send assistant transcript: {e}")

            # Send LLM response to Murf TTS WebSocket and stream base64 audio chunks to client
            try:
                import uuid
                from services.murf_ws_tts import murf_tts_ws
                async def stream_murf_audio():
                    context_id = str(uuid.uuid4())
                    async for base64_chunk in murf_tts_ws_stream(accumulated, context_id):
                        await self.websocket.send_json({
                            "type": "audio_chunk",
                            "data": base64_chunk
                        })
                        print(f"[Murf Audio Chunk Sent] {base64_chunk[:32]}... (len={len(base64_chunk)}) context_id={context_id}")
                async def murf_tts_ws_stream(text, context_id):
                    import json
                    import websockets
                    import os
                    MURF_WS_URL = "wss://api.murf.ai/v1/speech/stream-input"
                    MURF_API_KEY = os.getenv("MURF_API_KEY") or "ap2_da7fc32e-9572-4f87-ab2a-9c612f3cbde4"
                    async with websockets.connect(f"{MURF_WS_URL}?api-key={MURF_API_KEY}&sample_rate=44100&channel_type=MONO&format=WAV") as ws:
                        voice = "en-US-amara"
                        voice_config_msg = {
                            "voice_config": {
                                "voiceId": voice,
                                "style": "Conversational",
                                "rate": 0,
                                "pitch": 0,
                                "variation": 1
                            },
                            "context_id": context_id
                        }
                        await ws.send(json.dumps(voice_config_msg))
                        await ws.send(json.dumps({"text": text, "end": True, "context_id": context_id}))
                        while True:
                            message = await ws.recv()
                            data = json.loads(message)
                            if "audio" in data:
                                yield data["audio"]
                            if data.get("final"):
                                break
                asyncio.run_coroutine_threadsafe(stream_murf_audio(), self.loop)
            except Exception as e:
                print(f"[Murf TTS Error] {e}")
            if not event.turn_is_formatted:
                client.set_params(StreamingSessionParameters(format_turns=True))

    def on_termination(self, client, event: TerminationEvent):
        print(f"🛑 Session terminated after {event.audio_duration_seconds} s")

    def on_error(self, client, error: StreamingError):
        print("❌ Error:", error)

    def stream_audio(self, audio_chunk: bytes):
        self.client.stream(audio_chunk)

    def close(self):
        self.client.disconnect(terminate=True)
