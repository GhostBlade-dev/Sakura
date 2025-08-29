# 🗣️ Conversational Agent 🤖

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Node.js](https://img.shields.io/badge/Node.js-18%2B-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-teal.svg)
![Express](https://img.shields.io/badge/Express-Node.js-lightgrey.svg)

A voice-based conversational agent that lets users interact with an AI assistant using speech!  
The system records user audio, transcribes it, sends the transcript to a large language model (Gemini), and synthesizes the response using Murf AI text-to-speech.  
The frontend is a modern web UI, and the backend is built with FastAPI (Python) and Express (Node.js).

---

## 🚀 Technologies Used

- **Frontend:** HTML, CSS, JavaScript ([index.html](index.html)) 🎨
- **Backend (Python):** FastAPI, gTTS, requests, AssemblyAI, Gemini API, Murf AI API ([audio_server.py](audio_server.py)) 🐍
- **Backend (Node.js):** Express, node-fetch ([server.js](server.js)) 🟩
- **Other:** AssemblyAI for transcription, Murf AI for TTS, Gemini for LLM 🧠

---

## 🏗️ Architecture

- **Frontend:**  
  - 🎤 Records audio from the user.
  - 📤 Sends audio to the backend for processing.
  - 💬 Displays chat history and plays synthesized responses.

- **Backend (Python):**  
  - 📥 Handles audio uploads and session-based chat.
  - 📝 Transcribes audio using AssemblyAI.
  - 🗂️ Maintains chat history per session.
  - 🤖 Sends chat history to Gemini LLM for context-aware responses.
  - 🔊 Synthesizes responses using Murf AI TTS.
  - 🗃️ Serves static files and uploaded audio.

- **Backend (Node.js):**  
  - 🟩 Provides an Express server for Murf AI TTS generation (optional).

---

## ✨ Features

- 🗣️ Voice-based conversational interface
- 🧠 Session-based chat history for context retention
- ⚡ Real-time transcription and LLM response
- 🔊 High-quality TTS synthesis
- 🛡️ Fallback to gTTS or browser TTS if Murf AI fails
- 🖥️ Modern, responsive UI

---

## 📸 Screenshots

| Chat UI | Audio Upload |
|--------|-------------|
| ![Chat UI](https://user-images.githubusercontent.com/placeholder/chat-ui.png) | ![Audio Upload](https://user-images.githubusercontent.com/placeholder/audio-upload.png) |

*Replace the above URLs with your actual screenshots!*

---

## 🛠️ Setup & Running

### 📋 Prerequisites

- Python 3.8+
- Node.js 18+
- [pip](https://pip.pypa.io/en/stable/)

### 🔑 Environment Variables

Set the following environment variables (or update them directly in [`audio_server.py`](audio_server.py)):
- `GEMINI_API_KEY` (Google Gemini API key)
- `ASSEMBLYAI_API_KEY` (AssemblyAI API key)
- `MURF_API_KEY` (Murf AI API key)

You can export them in your shell or use a `.env` file.

### 📦 Install Python Dependencies

```sh
pip install fastapi uvicorn gtts requests
```

### 📦 Install Node.js Dependencies

```sh
npm install
```

### ▶️ Run the Python API Server

```sh
uvicorn audio_server:app --host 0.0.0.0 --port 8000
```

### ▶️ Run the Node.js Server (optional, for Murf AI TTS only)

```sh
node server.js
```

### 🌐 Access the Frontend

Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## 📡 API Endpoints

- `POST /agent/chat/{session_id}`: Upload audio, get LLM response and TTS audio
- `POST /tts/gtts`: Synthesize text using gTTS (fallback)
- `POST /tts/murf`: Synthesize text using Murf AI
- `POST /upload-audio`: Upload audio file
- `GET /uploads/{filename}`: Serve uploaded audio
- `GET /`: Serve frontend

See [`audio_server.py`](audio_server.py) for full API details.

---

## 📝 Notes

- 📁 Uploaded audio and synthesized files are stored in the `uploads/` directory.
- 🧠 The system uses in-memory chat history per session; restarting the server clears history.
- 🔒 For production, secure your API keys and use HTTPS.

---

## 📄 License

MIT License