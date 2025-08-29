console.log("Hello World from script.js");
const recordBtn = document.getElementById('recordBtn');
const chatHistoryDiv = document.getElementById('chatHistory');
const statusDiv = document.getElementById('uploadStatus');
let wsAudio;
let mediaRecorder;
let isRecording = false;

function addTextMessage(text, type) {
    const bubble = document.createElement('div');
    bubble.classList.add('bubble');
    bubble.classList.add(type === 'sent' ? 'assistant' : 'user');
    bubble.textContent = text;
    chatHistoryDiv.appendChild(bubble);
    chatHistoryDiv.scrollTop = chatHistoryDiv.scrollHeight;
}

function connectAudioWebSocket() {
    wsAudio = new WebSocket("ws://127.0.0.1:8000/ws/audio");
    wsAudio.binaryType = "arraybuffer";
    wsAudio.onopen = () => {
        statusDiv.textContent = "Audio WebSocket connected!";
        console.log("[WebSocket] Connected");
    };
    wsAudio.onclose = (event) => {
        statusDiv.textContent = "Audio WebSocket disconnected!";
        console.log("[WebSocket] Disconnected", event);
    };
    wsAudio.onerror = (event) => {
        statusDiv.textContent = "Audio WebSocket error!";
        console.error("[WebSocket] Error", event);
    };
    wsAudio.onmessage = (event) => {
        try {
            const msg = JSON.parse(event.data);
            console.log("[WebSocket message received]", msg);
            if (msg.type === "transcript" && msg.text) {
                addTextMessage(msg.text, 'sent');
                statusDiv.textContent = `🟢 End of turn. Transcript: "${msg.text}"`;
                setTimeout(() => {
                    statusDiv.textContent = "Ready.";
                }, 3000);
                console.log("[Transcript received]", msg.text);
            }
        } catch (e) {
            console.error("WebSocket message parse error", e, event.data);
        }
    };
}

recordBtn.addEventListener('click', async () => {
    if (!isRecording) {
        recordBtn.disabled = true;
        recordBtn.textContent = 'Listening...';
        recordBtn.classList.add('recording');
        statusDiv.textContent = 'Recording...';
        connectAudioWebSocket();
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();
            isRecording = true;
            recordBtn.disabled = false;
            recordBtn.textContent = 'Stop Recording';
            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0 && wsAudio && wsAudio.readyState === WebSocket.OPEN) {
                    wsAudio.send(e.data);
                }
            };
            mediaRecorder.onstop = () => {
                isRecording = false;
                recordBtn.textContent = 'Start Recording';
                recordBtn.classList.remove('recording');
                recordBtn.disabled = false;
                if (wsAudio && wsAudio.readyState === WebSocket.OPEN) {
                    wsAudio.send("END");
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
