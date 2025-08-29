import asyncio
import websockets
import json
import base64

MURF_WS_URL = "wss://api.murf.ai/v1/speech/stream-input"
MURF_API_KEY = "ap2_da7fc32e-9572-4f87-ab2a-9c612f3cbde4"  # Replace with your actual Murf API key
STATIC_CONTEXT_ID = "static-context-001"  # Use a static context_id to avoid context limit errors

async def murf_tts_ws(text: str, voice: str = "en-US-WilliamNeural"):
    async with websockets.connect(f"{MURF_WS_URL}?api-key={MURF_API_KEY}&sample_rate=44100&channel_type=MONO&format=WAV") as ws:
        # Always use a valid Murf voiceId
        voice = "en-US-amara"
        voice_config_msg = {
            "voice_config": {
                "voiceId": voice,
                "style": "Conversational",
                "rate": 0,
                "pitch": 0,
                "variation": 1
            }
        }
        print(f"[Murf] Sending voice config: {voice_config_msg}")
        await ws.send(json.dumps(voice_config_msg))

        text_msg = {
            "text": text,
            "end": True
        }
        print(f"[Murf] Sending text: {text_msg}")
        await ws.send(json.dumps(text_msg))

        audio_base64 = ""
        try:
            while True:
                message = await ws.recv()
                print(f"[Murf] Received message: {message}")
                data = json.loads(message)
                if "audio" in data:
                    audio_base64 = data["audio"]
                    print(f"[Murf Audio Base64] {audio_base64}")
                if data.get("final"):
                    print("[Murf] Final message received, closing stream.")
                    break
        except Exception as e:
            print(f"[Murf WS Error] {e}")
        return audio_base64

# For synchronous usage in FastAPI
import threading

def run_murf_tts(text, voice="en-US-WilliamNeural"):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(murf_tts_ws(text, voice))