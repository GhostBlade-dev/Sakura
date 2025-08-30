# 🌸 Sakura: Your Real-Time Voice AI Companion

![License: MIT](https://img.shields.io/badge/License-MIT-pink.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-pink.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-pink.svg)

Welcome to Sakura! She’s a gentle, caring, and emotionally intelligent voice agent who listens, understands, and responds with warmth. Sakura can answer your questions, fetch real-time weather, search the web, and chat with you using her own voice—all in your browser!

---

## ✨ Features
- 🌸 **Adorable Sakura UI:** Cozy, pastel gradients, dark mode, and a glowing, pillowy chat container.
- 💖 **Breathing Animations:** Smooth breathing effect for the chat container and Sakura avatar, making the UI feel alive and comforting.
- 🐾 **Animated Emoji Overlay:** Floating cute emojis (✨ 💖 🌸 🐾 🐱) with playful, gentle movement.
- 🎀 **Cute Modal Dialog:** Enter API keys in a rounded, pastel modal dialog, triggered by a kawaii button under Sakura’s avatar.
- 🫧 **Cozy Chat Bubbles:** Soft, rounded bubbles for both user and assistant, with pastel gradients and gentle shadows.
- 🎤 **Voice chat:** Speak to Sakura and get instant responses.
- 🌦️ **Weather skill:** Ask Sakura about the weather—she’ll fetch it live!
- 🔎 **Web search:** Sakura can search the web for you in real time.
- 🧠 **Gemini LLM:** Context-aware, persona-driven answers.
- 🔊 **Murf TTS:** Sakura’s voice is generated and streamed for seamless playback.
- 🗝️ **Config sidebar:** Enter your own API keys for privacy and control.
- 🌐 **Public HTTPS hosting:** Secure and shareable via Render.com.

---

## 🌸 Sakura Voice Agent UI Preview

![Sakura UI Screenshot](sakura-ui.png)

---

## 📝 Latest Updates
- 🌸 Breathing animation for avatar and container
- 🐾 Animated pastel/dark background gradient
- 💖 Floating emoji overlay with improved animation
- 🎀 Cute modal dialog for API key entry
- 🫧 Cozy, pillowy container with pastel glow
- 🐱 Improved assistant bubble visibility
- 🎤 Cute, pulsing recording button
- 📱 Responsive and accessible design

---

## 🏗️ Architecture
- **Frontend:** HTML, CSS, JavaScript (see `index.html`, `static/script.js`)
- **Backend:** FastAPI (Python), Murf TTS, Gemini LLM, AssemblyAI, WeatherAPI, Tavily
- **No Node.js, no .env required!**

---

## 🛠️ Setup & Usage

### 🌸 Try Sakura Online
Sakura is live and ready to chat:
**[https://sakura-6seg.onrender.com](https://sakura-6seg.onrender.com)**

Just open the link, enter your API keys in the sidebar, and start talking!

### 🏡 Run Locally
1. **Clone the repo:**
   ```sh
   git clone https://github.com/GhostBlade-dev/Sakura.git
   cd Sakura
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Start the server:**
   ```sh
   uvicorn audio_server:app --host 0.0.0.0 --port 8000
   ```
4. **Open your browser:**
   [http://localhost:8000](http://localhost:8000)

### 🔑 API Keys
- Enter your Gemini, AssemblyAI, Murf, WeatherAPI, and Tavily keys in the sidebar or modal dialog
- Sakura never stores your keys—they’re used only for your session

---

## 📡 API Endpoints
- `POST /agent/chat/{session_id}`: Upload audio, get LLM response and TTS audio
- `POST /tts/gtts`: Synthesize text using gTTS (fallback)
- `POST /tts/murf`: Synthesize text using Murf AI
- `POST /upload-audio`: Upload audio file
- `GET /uploads/{filename}`: Serve uploaded audio
- `GET /`: Serve frontend

---

## 💖 Screenshots
*Add your own screenshots here to show off Sakura’s cuteness!*

---

## 📄 License
MIT License

---

> Made with love by Sakura and you! 🌸