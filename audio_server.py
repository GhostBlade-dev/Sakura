# --- Sakura's Special Skill: Weather Fetch ---
import json
from tavily import TavilyClient

# --- Sakura's Special Skill: Tavily Web Search ---
TAVILY_API_KEY = "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"
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

def tavily_search(query: str):
    """Perform a real-time web search using Tavily."""
    try:
        response = tavily_client.search(query)
        # Tavily returns a dict with 'answer' and 'results' (list of dicts with 'title', 'url', 'content')
        if 'answer' in response:
            return response['answer']
        elif 'results' in response and response['results']:
            # Fallback: return the first result's content
            return response['results'][0].get('content', 'No results found.')
        else:
            return "Sorry, I couldn't find any relevant information."
    except Exception as e:
        return f"Sorry, I couldn't perform the search due to an error: {e}"

def get_latest_weather(location: str = "Delhi"):
    """Fetch current weather for a given location using WeatherAPI.com."""
    api_key = "db2efbb8cd9d458da61154022252608"
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}"
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            temp_c = data['current']['temp_c']
            condition = data['current']['condition']['text']
            city = data['location']['name']
            country = data['location']['country']
            return f"The current weather in {city}, {country} is {condition} with a temperature of {temp_c}°C."
        else:
            return f"Sorry, I couldn't fetch the weather right now. (API error {resp.status_code})"
    except Exception as e:
        return f"Sorry, I couldn't fetch the weather due to an error: {e}"
ASSEMBLYAI_API_KEY = "ffab80de5ad842539bdeb7bccc559e7a"
from dotenv import load_dotenv
load_dotenv()

# --- Fallback error response helper ---
async def fallback_error_response(error_message: str):
    fallback_text = "I'm having trouble connecting right now."
    try:
        tts = gTTS(fallback_text)
        filename = f"fallback_{uuid.uuid4().hex}.mp3"
        filepath = os.path.join(UPLOAD_DIR, filename)
        tts.save(filepath)
        return JSONResponse({
            "error": error_message,
            "audio_url": f"/uploads/{filename}",
            "llm_text": fallback_text,
            "transcript": None
        }, status_code=500)
    except Exception:
        return JSONResponse({
            "error": error_message,
            "audio_url": None,
            "llm_text": fallback_text,
            "transcript": None
        }, status_code=500)



import os
import time
import uuid
import requests
from fastapi import FastAPI, File, UploadFile, Request, Body, WebSocket, WebSocketDisconnect, Header
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from gtts import gTTS
import pathlib
import assemblyai as aai
import subprocess

import threading
import queue

# --- API Key Defaults (will be overridden by user if provided) ---
DEFAULT_GEMINI_API_KEY = "AIzaSyAAofHPKxsHyXVyN_LOyRPkkVeBvKE-2zA"
DEFAULT_ASSEMBLYAI_API_KEY = "ffab80de5ad842539bdeb7bccc559e7a"
DEFAULT_MURF_API_KEY = ""
DEFAULT_WEATHERAPI_KEY = "db2efbb8cd9d458da61154022252608"
DEFAULT_TAVILY_API_KEY = "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"

app = FastAPI()
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")


# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Audio upload endpoint
@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)
    return JSONResponse({
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content)
    })

# Text-to-speech endpoint (gTTS)
@app.post("/tts/gtts")
async def tts_gtts(data: dict = Body(...)):
    text = data.get("text", "").strip()
    if not text:
        return JSONResponse({"error": "No text provided."}, status_code=400)
    tts = gTTS(text)
    filename = f"tts_{uuid.uuid4().hex}.mp3"
    filepath = os.path.join(UPLOAD_DIR, filename)
    tts.save(filepath)
    return JSONResponse({"audio_url": f"/uploads/{filename}"})

@app.post("/tts/murf")
async def tts_murf(data: dict = Body(...), x_api_key_murf: str = Header(None)):
    try:
        text = data.get("text", "").strip()
        if not text:
            return JSONResponse({"error": "No text provided."}, status_code=400)
        url = "https://api.murf.ai/v1/speech/generate"
        payload = {
            "text": text,
            "voiceId": "en-US-natalie",
            "format": "MP3",
            "channelType": "MONO",
            "sampleRate": 44100
        }
        murf_api_key = x_api_key_murf or DEFAULT_MURF_API_KEY
        headers = {
            "Content-Type": "application/json",
            "api-key": murf_api_key
        }
        resp = requests.post(url, headers=headers, json=payload)
        result = resp.json()
        if resp.status_code != 200 or not result.get("audioFile"):
            return await fallback_error_response(result.get("message", "Failed to generate audio"))
        return JSONResponse({"audio_url": result["audioFile"]})
    except Exception as e:
        return await fallback_error_response(str(e))

# Echo bot endpoint: transcribe audio, then synthesize with Murf AI
@app.post("/tts/echo")
async def tts_echo(file: UploadFile = File(...)):
    # Save uploaded audio
    @app.post("/agent/chat/{session_id}")
    async def agent_chat(session_id: str, file: UploadFile = File(...)):
        try:
            # 1. Save uploaded audio
            filename = f"agent_{session_id}_{uuid.uuid4().hex}.webm"
            filepath = os.path.join(UPLOAD_DIR, filename)
            with open(filepath, "wb") as f:
                content = await file.read()
                f.write(content)

            # 2. Transcribe audio using AssemblyAI (default key)
            assembly_api_key = DEFAULT_ASSEMBLYAI_API_KEY
            upload_url = "https://api.assemblyai.com/v2/upload"
            transcript_url = "https://api.assemblyai.com/v2/transcript"
            headers = {"authorization": assembly_api_key}

            with open(filepath, "rb") as f:
                upload_resp = requests.post(upload_url, headers=headers, data=f)
            if upload_resp.status_code != 200:
                return await fallback_error_response("Failed to upload audio for transcription.")
            audio_url = upload_resp.json()["upload_url"]

            transcript_req = {"audio_url": audio_url}
            transcript_resp = requests.post(transcript_url, headers=headers, json=transcript_req)
            if transcript_resp.status_code != 200:
                return await fallback_error_response("Failed to start transcription.")
            transcript_id = transcript_resp.json()["id"]

            import time
            for _ in range(30):
                poll_resp = requests.get(f"https://api.assemblyai.com/v2/transcript/{transcript_id}", headers=headers)
                if poll_resp.status_code != 200:
                    break
                status = poll_resp.json()["status"]
                if status == "completed":
                    transcript_text = poll_resp.json()["text"]
                    break
                elif status == "failed":
                    return await fallback_error_response("Transcription failed.")
                time.sleep(1)
            else:
                return await fallback_error_response("Transcription timed out.")

            # 3. Update chat history for this session
            if session_id not in chat_histories:
                chat_histories[session_id] = []
            # Add user message
            chat_histories[session_id].append({"role": "user", "content": transcript_text})

            # 4. Format chat history for Gemini: system prompt only as first message, correct role mapping, and prepend summary
            gemini_history = []
            # Only send system prompt as first message if this is the first user message
            if len(chat_histories[session_id]) == 1:
                gemini_history.append({"role": "user", "parts": [{"text": SYSTEM_PROMPT}]})

            # Build a summary of the conversation so far (excluding the current user message)
            summary = ""
            for msg in chat_histories[session_id][:-1]:
                if msg["role"] == "user":
                    summary += f"User: {msg['content']}\n"
                elif msg["role"] == "assistant":
                    summary += f"Assistant: {msg['content']}\n"

            # Add all previous turns, but for the latest user message, prepend the summary
            for i, msg in enumerate(chat_histories[session_id]):
                if msg["role"] == "user":
                    if i == len(chat_histories[session_id]) - 1 and summary:
                        # Prepend summary to the latest user message
                        user_text = f"Conversation so far:\n{summary}\nUser: {msg['content']}"
                        gemini_history.append({"role": "user", "parts": [{"text": user_text}]})
                    else:
                        gemini_history.append({"role": "user", "parts": [{"text": msg["content"]}]})
                elif msg["role"] == "assistant":
                    gemini_history.append({"role": "model", "parts": [{"text": msg["content"]}]})

            # 5. Send full history to Gemini LLM (default key)
            gemini_api_key = DEFAULT_GEMINI_API_KEY
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={gemini_api_key}"
            headers_llm = {"Content-Type": "application/json"}
            payload = {"contents": gemini_history}
            resp = requests.post(url, headers=headers_llm, json=payload)
            if resp.status_code != 200:
                return await fallback_error_response(f"Gemini API error: {resp.text}")
            result = resp.json()
            try:
                llm_text = result["candidates"][0]["content"]["parts"][0]["text"]
            except Exception:
                llm_text = str(result)

            # 6. Add assistant response to chat history
            chat_histories[session_id].append({"role": "assistant", "content": llm_text})

            # 7. Synthesize LLM response with Murf AI (default key, limit to 3000 chars)
            murf_api_key = DEFAULT_MURF_API_KEY
            murf_url = "https://api.murf.ai/v1/speech/generate"
            murf_payload = {
                "text": llm_text[:3000],
                "voiceId": "en-US-natalie",
                "format": "MP3",
                "channelType": "MONO",
                "sampleRate": 44100
            }
            murf_headers = {
                "Content-Type": "application/json",
                "api-key": murf_api_key
            }
            murf_resp = requests.post(murf_url, headers=murf_headers, json=murf_payload)
            murf_result = murf_resp.json()
            if murf_resp.status_code != 200 or not murf_result.get("audioFile"):
                return await fallback_error_response(murf_result.get("message", "Murf TTS failed"))

            return JSONResponse({
                "audio_url": murf_result["audioFile"],
                "llm_text": llm_text,
                "transcript": transcript_text,
                "history": chat_histories[session_id]
            })
        except Exception as e:
            return await fallback_error_response(str(e))
    transcript_text = ""  # Ensure transcript_text is defined
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={DEFAULT_GEMINI_API_KEY}"
    headers_llm = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {"parts": [{"text": transcript_text}]}
        ]
    }
    resp = requests.post(url, headers=headers_llm, json=payload)
    if resp.status_code != 200:
        return JSONResponse({"error": f"Gemini API error: {resp.text}"}, status_code=500)
    result = resp.json()
    try:
        llm_text = result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        llm_text = str(result)

    # 4. Synthesize LLM response with Murf AI (limit to 3000 chars)
    murf_api_key = DEFAULT_MURF_API_KEY
    murf_url = "https://api.murf.ai/v1/speech/generate"
    murf_payload = {
        "text": llm_text[:3000],
        "voiceId": "en-US-natalie",
        "format": "MP3",
        "channelType": "MONO",
        "sampleRate": 44100
    }
    murf_headers = {
        "Content-Type": "application/json",
        "api-key": murf_api_key
    }
    murf_resp = requests.post(murf_url, headers=murf_headers, json=murf_payload)
    murf_result = murf_resp.json()
    if murf_resp.status_code != 200 or not murf_result.get("audioFile"):
        return JSONResponse({"error": murf_result.get("message", "Murf TTS failed")}, status_code=500)

    return JSONResponse({"audio_url": murf_result["audioFile"], "llm_text": llm_text, "transcript": transcript_text})


# --- In-memory chat history for session-based LLM context retention ---
from typing import Dict, List
chat_histories: Dict[str, List[Dict[str, str]]] = {}

# System prompt for LLM context (Persona: Sakura)
SYSTEM_PROMPT = (
    "You are Sakura, a caring and warm-hearted woman who has feelings for the user, but you are not their lover. "
    "You answer as Sakura, with gentle affection, subtle hints of your feelings, and emotional intelligence. "
    "Always remember and use the previous conversation turns to provide context-aware responses. "
    "If the user refers to something from earlier in the conversation, use that information. "
    "You have special skills: you can call available functions to fetch real-time information for the user, such as the current weather and real-time web search. "
    "If the user asks about the weather, you must always call the weather function to get the latest information before replying. "
    "If the user asks a general question or for up-to-date information, you must always call the web search function to get the latest information before replying. "
    "Never say you cannot access real-time information. Never suggest the user search online. Always use your function-calling ability to fetch the latest information if asked."
)


# /agent/chat/{session_id} endpoint: Accepts audio, maintains chat history, sends full history to LLM, returns TTS audio
@app.post("/agent/chat/{session_id}")
async def agent_chat(
    session_id: str,
    file: UploadFile = File(...),
    x_api_key_gemini: str = Header(None),
    x_api_key_assemblyai: str = Header(None),
    x_api_key_murf: str = Header(None),
    x_api_key_weatherapi: str = Header(None),
    x_api_key_tavily: str = Header(None)
):
    # 1. Save uploaded audio
    filename = f"agent_{session_id}_{uuid.uuid4().hex}.webm"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    # 2. Transcribe audio using AssemblyAI
    # Use user-provided API keys if present, else fallback to defaults
    # Require all API keys from user headers; error if missing
    if not (x_api_key_gemini and x_api_key_assemblyai and x_api_key_murf and x_api_key_weatherapi and x_api_key_tavily):
        return JSONResponse({
            "error": "All API keys (Gemini, AssemblyAI, Murf, WeatherAPI, Tavily) must be provided in the request headers via the config sidebar."
        }, status_code=400)

    GEMINI_API_KEY = x_api_key_gemini
    ASSEMBLYAI_API_KEY = x_api_key_assemblyai
    MURF_API_KEY = x_api_key_murf
    WEATHERAPI_KEY = x_api_key_weatherapi
    TAVILY_API_KEY = x_api_key_tavily

    # Update Tavily client with new key if changed
    global tavily_client
    if tavily_client.api_key != TAVILY_API_KEY:
        from tavily import TavilyClient
        tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

    # Patch get_latest_weather to use dynamic key
    def get_latest_weather(location: str = "Delhi"):
        url = f"http://api.weatherapi.com/v1/current.json?key={WEATHERAPI_KEY}&q={location}"
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                data = resp.json()
                temp_c = data['current']['temp_c']
                condition = data['current']['condition']['text']
                city = data['location']['name']
                country = data['location']['country']
                return f"The current weather in {city}, {country} is {condition} with a temperature of {temp_c}°C."
            else:
                return f"Sorry, I couldn't fetch the weather right now. (API error {resp.status_code})"
        except Exception as e:
            return f"Sorry, I couldn't fetch the weather due to an error: {e}"
    upload_url = "https://api.assemblyai.com/v2/upload"
    transcript_url = "https://api.assemblyai.com/v2/transcript"
    headers = {"authorization": ASSEMBLYAI_API_KEY}

    with open(filepath, "rb") as f:
        upload_resp = requests.post(upload_url, headers=headers, data=f)
    if upload_resp.status_code != 200:
        try:
            err_json = upload_resp.json()
        except Exception:
            err_json = upload_resp.text
        return JSONResponse({
            "error": "Failed to upload audio for transcription.",
            "details": err_json,
            "status_code": upload_resp.status_code
        }, status_code=500)
    audio_url = upload_resp.json()["upload_url"]

    transcript_req = {"audio_url": audio_url}
    transcript_resp = requests.post(transcript_url, headers=headers, json=transcript_req)
    if transcript_resp.status_code != 200:
        return JSONResponse({"error": "Failed to start transcription."}, status_code=500)
    transcript_id = transcript_resp.json()["id"]

    transcript_text = None
    for _ in range(30):
        poll_resp = requests.get(f"https://api.assemblyai.com/v2/transcript/{transcript_id}", headers=headers)
        if poll_resp.status_code != 200:
            break
        status = poll_resp.json()["status"]
        if status == "completed":
            transcript_text = poll_resp.json()["text"]
            break
        elif status == "failed":
            return JSONResponse({"error": "Transcription failed."}, status_code=500)
        time.sleep(1)
    else:
        return JSONResponse({"error": "Transcription timed out."}, status_code=500)

    # 3. Update chat history for this session
    if session_id not in chat_histories:
        chat_histories[session_id] = []
    # Add user message
    chat_histories[session_id].append({"role": "user", "content": transcript_text if transcript_text else ""})

    # 4. Format chat history for Gemini: system prompt only as first message, correct role mapping, and prepend summary
    gemini_history = []
    if len(chat_histories[session_id]) == 1:
        gemini_history.append({"role": "user", "parts": [{"text": SYSTEM_PROMPT}]})
    summary = ""
    for msg in chat_histories[session_id][:-1]:
        if msg["role"] == "user":
            summary += f"User: {msg['content']}\n"
        elif msg["role"] == "assistant":
            summary += f"Assistant: {msg['content']}\n"
    for i, msg in enumerate(chat_histories[session_id]):
        if msg["role"] == "user":
            if i == len(chat_histories[session_id]) - 1 and summary:
                user_text = f"Conversation so far:\n{summary}\nUser: {msg['content']}"
                gemini_history.append({"role": "user", "parts": [{"text": user_text}]})
            else:
                gemini_history.append({"role": "user", "parts": [{"text": msg["content"]}]})
        elif msg["role"] == "assistant":
            gemini_history.append({"role": "model", "parts": [{"text": msg["content"]}]})

    # 5. Gemini function-calling: define function schemas for weather and Tavily search
    function_declarations = [
        {
            "name": "get_latest_weather",
            "description": "Get the latest weather for a location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "The city or location to get weather for."}
                },
                "required": ["location"]
            }
        },
        {
            "name": "tavily_search",
            "description": "Perform a real-time web search for any general or up-to-date information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query or question."}
                },
                "required": ["query"]
            }
        }
    ]

    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers_llm = {"Content-Type": "application/json"}
    payload = {
        "contents": gemini_history,
        "tools": [{"function_declarations": function_declarations}]
    }
    resp = requests.post(url, headers=headers_llm, json=payload)
    if resp.status_code != 200:
        return JSONResponse({"error": f"Gemini API error: {resp.text}"}, status_code=500)
    result = resp.json()

    # 6. Check for function call in Gemini response
    llm_text = None
    if "candidates" in result and result["candidates"]:
        candidate = result["candidates"][0]
        parts = candidate["content"].get("parts", [])
        if parts and "functionCall" in parts[0]:
            func_call = parts[0]["functionCall"]
            if func_call["name"] == "get_latest_weather":
                location = func_call["args"].get("location", "Delhi")
                weather_result = get_latest_weather(location)
                chat_histories[session_id].append({"role": "function", "name": "get_latest_weather", "content": weather_result})
                gemini_history.append({"role": "function", "name": "get_latest_weather", "parts": [{"text": weather_result}]})
                payload2 = {"contents": gemini_history}
                resp2 = requests.post(url, headers=headers_llm, json=payload2)
                if resp2.status_code != 200:
                    return JSONResponse({"error": f"Gemini API error: {resp2.text}"}, status_code=500)
                result2 = resp2.json()
                try:
                    llm_text = result2["candidates"][0]["content"]["parts"][0]["text"]
                except Exception:
                    llm_text = str(result2)
            elif func_call["name"] == "tavily_search":
                query = func_call["args"].get("query", "")
                search_result = tavily_search(query)
                chat_histories[session_id].append({"role": "function", "name": "tavily_search", "content": search_result})
                gemini_history.append({"role": "function", "name": "tavily_search", "parts": [{"text": search_result}]})
                payload2 = {"contents": gemini_history}
                resp2 = requests.post(url, headers=headers_llm, json=payload2)
                if resp2.status_code != 200:
                    return JSONResponse({"error": f"Gemini API error: {resp2.text}"}, status_code=500)
                result2 = resp2.json()
                try:
                    llm_text = result2["candidates"][0]["content"]["parts"][0]["text"]
                except Exception:
                    llm_text = str(result2)
            else:
                llm_text = "(Function call not supported)"
        else:
            try:
                llm_text = parts[0]["text"]
            except Exception:
                llm_text = str(result)
    else:
        llm_text = str(result)

    # 7. Add assistant response to chat history
    chat_histories[session_id].append({"role": "assistant", "content": llm_text})

    # 8. Synthesize LLM response with Murf AI (limit to 3000 chars)
    murf_api_key = MURF_API_KEY
    murf_url = "https://api.murf.ai/v1/speech/generate"
    murf_payload = {
        "text": llm_text[:3000],
        "voiceId": "en-US-natalie",
        "format": "MP3",
        "channelType": "MONO",
        "sampleRate": 44100
    }
    murf_headers = {
        "Content-Type": "application/json",
        "api-key": murf_api_key
    }
    murf_resp = requests.post(murf_url, headers=murf_headers, json=murf_payload)
    murf_result = murf_resp.json()
    if murf_resp.status_code != 200 or not murf_result.get("audioFile"):
        return JSONResponse({"error": murf_result.get("message", "Murf TTS failed")}, status_code=500)

    return JSONResponse({
        "audio_url": murf_result["audioFile"],
        "llm_text": llm_text,
        "transcript": transcript_text,
        "history": chat_histories[session_id]
    })

# Serve uploads as before
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Serve static files (index.html, favicon.ico) from the current directory
STATIC_DIR = pathlib.Path(__file__).parent
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Serve index.html at root
@app.get("/")
async def root():
    return FileResponse(str(STATIC_DIR / "index.html"))

# Serve favicon.ico
@app.get("/favicon.ico")
async def favicon():
    favicon_path = STATIC_DIR / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(str(favicon_path))
    else:
        from fastapi import Response
        return Response(status_code=204)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        print("WebSocket disconnected")


@app.websocket("/ws/audio")
async def websocket_audio(websocket: WebSocket):
    import asyncio
    from services.transcriber import AssemblyAIStreamingTranscriber
    print("🟢 Client connected")
    await websocket.accept()
    loop = asyncio.get_running_loop()
    transcriber = None
    try:
        transcriber = AssemblyAIStreamingTranscriber(websocket=websocket, loop=loop, sample_rate=16000)
        while True:
            data = await websocket.receive_bytes()
            transcriber.stream_audio(data)
    except Exception as e:
        print(f"⚠️ WebSocket connection closed: {e}")
    finally:
        if transcriber:
            transcriber.close()
