// --- API Key Config ---
const apiKeys = {
    gemini: localStorage.getItem('apiKey-gemini') || '',
    assemblyai: localStorage.getItem('apiKey-assemblyai') || '',
    murf: localStorage.getItem('apiKey-murf') || '',
    weatherapi: localStorage.getItem('apiKey-weatherapi') || '',
    tavily: localStorage.getItem('apiKey-tavily') || ''
};

function updateApiKeyInputs() {
    document.getElementById('config-gemini').value = apiKeys.gemini;
    document.getElementById('config-assemblyai').value = apiKeys.assemblyai;
    document.getElementById('config-murf').value = apiKeys.murf;
    document.getElementById('config-weatherapi').value = apiKeys.weatherapi;
    document.getElementById('config-tavily').value = apiKeys.tavily;
}

function saveApiKeys() {
    apiKeys.gemini = document.getElementById('config-gemini').value.trim();
    apiKeys.assemblyai = document.getElementById('config-assemblyai').value.trim();
    apiKeys.murf = document.getElementById('config-murf').value.trim();
    apiKeys.weatherapi = document.getElementById('config-weatherapi').value.trim();
    apiKeys.tavily = document.getElementById('config-tavily').value.trim();
    localStorage.setItem('apiKey-gemini', apiKeys.gemini);
    localStorage.setItem('apiKey-assemblyai', apiKeys.assemblyai);
    localStorage.setItem('apiKey-murf', apiKeys.murf);
    localStorage.setItem('apiKey-weatherapi', apiKeys.weatherapi);
    localStorage.setItem('apiKey-tavily', apiKeys.tavily);
    document.getElementById('save-status').textContent = 'Saved!';
    setTimeout(() => document.getElementById('save-status').textContent = '', 1500);
}

document.getElementById('save-api-keys').onclick = saveApiKeys;
updateApiKeyInputs();

// --- Attach API keys to requests ---
function getApiKeyHeaders() {
    return {
        'x-api-key-gemini': apiKeys.gemini,
        'x-api-key-assemblyai': apiKeys.assemblyai,
        'x-api-key-murf': apiKeys.murf,
        'x-api-key-weatherapi': apiKeys.weatherapi,
        'x-api-key-tavily': apiKeys.tavily
    };
}

// ...existing code...

console.log("Hello World from static/script.js");
const recordBtn = document.getElementById('recordBtn');
const chatHistoryDiv = document.getElementById('chatHistory');
const statusDiv = document.getElementById('uploadStatus');
let wsAudio;
let mediaRecorder;
let isRecording = false;

    function addTextMessage(text, type, is_assistant) {
        const bubble = document.createElement('div');
        bubble.classList.add('bubble');
        if (is_assistant === true) {
            bubble.classList.add('assistant'); // assistant: left
            bubble.style.alignSelf = 'flex-start';
        } else {
            bubble.classList.add('user'); // user: right
            bubble.style.alignSelf = 'flex-end';
        }
        bubble.textContent = text;
        chatHistoryDiv.appendChild(bubble);
        chatHistoryDiv.scrollTop = chatHistoryDiv.scrollHeight;
    }

function connectAudioWebSocket() {
    console.log('[Client] Opening new WebSocket for audio stream...');
    // Dynamically set WebSocket URL based on environment
    let wsUrl;
    if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
        wsUrl = "ws://127.0.0.1:8000/ws/audio";
    } else {
        // Use wss and current host for production (Render)
        wsUrl = `wss://${window.location.host}/ws/audio`;
    }
    wsAudio = new WebSocket(wsUrl);
    wsAudio.binaryType = "arraybuffer";
    window._murfAudioChunks = [];
    window._murfBase64AudioChunks = [];
    window._murfAudioContext = null;
    window._murfPlayheadTime = 0;
    window._murfIsPlaying = false;
    window._murfWavHeaderSet = true;
    const SAMPLE_RATE = 44100;
    wsAudio.onopen = () => {
        statusDiv.textContent = "Audio WebSocket connected!";
        console.log('[WebSocket] Connected');
        console.log('[Client] WebSocket onopen fired. Creating new AudioContext.');
        window._murfAudioContext = new (window.AudioContext || window.webkitAudioContext)();
        window._murfPlayheadTime = window._murfAudioContext.currentTime;
    };
    wsAudio.onerror = (event) => {
        console.error('[WebSocket] Error:', event);
    };
    wsAudio.onclose = (event) => {
        console.log('[WebSocket] Closed:', event);
        console.log('[Client] WebSocket onclose fired. Event:', event);
    };
    function base64ToPCMFloat32(base64) {
        let binary = atob(base64);
        const offset = window._murfWavHeaderSet ? 44 : 0;
        window._murfWavHeaderSet = false;
        const length = binary.length - offset;
        const buffer = new ArrayBuffer(length);
        const byteArray = new Uint8Array(buffer);
        for (let i = 0; i < byteArray.length; i++) {
            byteArray[i] = binary.charCodeAt(i + offset);
        }
        const view = new DataView(byteArray.buffer);
        const sampleCount = byteArray.length / 2;
        const float32Array = new Float32Array(sampleCount);
        for (let i = 0; i < sampleCount; i++) {
            const int16 = view.getInt16(i * 2, true);
            float32Array[i] = int16 / 32768;
        }
        return float32Array;
    }
    function chunkPlay() {
        if (window._murfAudioChunks.length > 0) {
            const chunk = window._murfAudioChunks.shift();
            console.log('[Client] Playing audio chunk. Remaining:', window._murfAudioChunks.length);
            if (window._murfAudioContext.state === "suspended") {
                window._murfAudioContext.resume();
            }
            const buffer = window._murfAudioContext.createBuffer(1, chunk.length, SAMPLE_RATE);
            buffer.copyToChannel(chunk, 0);
            const source = window._murfAudioContext.createBufferSource();
            source.buffer = buffer;
            source.connect(window._murfAudioContext.destination);
            const now = window._murfAudioContext.currentTime;
            if (window._murfPlayheadTime < now) {
                window._murfPlayheadTime = now + 0.05;
            }
            source.start(window._murfPlayheadTime);
            window._murfPlayheadTime += buffer.duration;
            if (window._murfAudioChunks.length > 0) {
                chunkPlay();
            } else {
                window._murfIsPlaying = false;
                console.log('[Client] Finished playing all audio chunks for this turn.');
            }
        }
    }
    wsAudio.onmessage = (event) => {
        try {
            const msg = JSON.parse(event.data);
            console.log('[Client] WebSocket message received:', msg);
            if (msg.type === "transcript") {
                if (msg.text) {
                    addTextMessage(msg.text, msg.is_assistant ? 'sent' : 'user', msg.is_assistant);
                }
                statusDiv.textContent = msg.end_of_turn
                    ? `🟢 End of turn.`
                    : 'Transcribing...';
                if (msg.end_of_turn && wsAudio && wsAudio.readyState === WebSocket.OPEN) {
                    setTimeout(() => {
                        statusDiv.textContent = "Ready.";
                    }, 3000);
                    console.log('[Client] Closing WebSocket after end_of_turn.');
                    wsAudio.close();
                }
            } else if (msg.type === "audio_chunk") {
                // Streaming audio playback logic
                console.log(`[Client] Audio chunk received. Decoding and queuing for playback. idx=${window._murfBase64AudioChunks.length}, len=${msg.data.length}`);
                const float32Array = base64ToPCMFloat32(msg.data);
                window._murfAudioChunks.push(float32Array);
                window._murfBase64AudioChunks.push(msg.data);
                // Start playback if not already playing
                if (!window._murfIsPlaying) {
                    window._murfIsPlaying = true;
                    window._murfAudioContext.resume();
                    console.log('[Client] Starting chunk playback.');
                    chunkPlay();
                }
            }
        } catch (e) {
            console.error("WebSocket message parse error", e, event.data);
        }
    };
}

recordBtn.addEventListener('click', async () => {
    if (!isRecording) {
        // Always reset playback state and open a new WebSocket for each turn
        recordBtn.disabled = true;
        recordBtn.textContent = 'Listening...';
        recordBtn.classList.add('recording');
        statusDiv.textContent = 'Recording...';

        // Reset playback state
        if (window._murfAudioContext && window._murfAudioContext.state !== 'closed') {
            window._murfAudioContext.close();
        }
        window._murfAudioContext = null;
        window._murfAudioChunks = [];
        window._murfBase64AudioChunks = [];
        window._murfPlayheadTime = 0;
        window._murfIsPlaying = false;
        window._murfWavHeaderSet = true;

        connectAudioWebSocket();
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
            const source = audioContext.createMediaStreamSource(stream);
            const processor = audioContext.createScriptProcessor(4096, 1, 1);
            source.connect(processor);
            processor.connect(audioContext.destination);
            isRecording = true;
            recordBtn.disabled = false;
            recordBtn.textContent = 'Stop Recording';
            statusDiv.textContent = 'Recording...';

            processor.onaudioprocess = (e) => {
                if (!isRecording) return;
                const input = e.inputBuffer.getChannelData(0);
                // Convert Float32Array [-1,1] to Int16 PCM
                const pcm16 = new Int16Array(input.length);
                for (let i = 0; i < input.length; i++) {
                    let s = Math.max(-1, Math.min(1, input[i]));
                    pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
                }
                if (wsAudio && wsAudio.readyState === WebSocket.OPEN) {
                    wsAudio.send(pcm16.buffer);
                }
            };

            // Stop logic
            recordBtn.onclick = async () => {
                if (isRecording) {
                    isRecording = false;
                    processor.disconnect();
                    source.disconnect();
                    stream.getTracks().forEach(track => track.stop());
                    audioContext.close();
                    recordBtn.textContent = 'Start Recording';
                    statusDiv.textContent = 'Recording stopped.';
                    recordBtn.classList.remove('recording');
                }
            };
        } catch (err) {
            statusDiv.textContent = 'Microphone access denied or error: ' + err.message;
            recordBtn.disabled = false;
            recordBtn.classList.remove('recording');
            recordBtn.textContent = 'Start Recording';
        }
    } else {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
        }
    }
});
