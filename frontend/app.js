const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const output = document.getElementById("output");

const ctx = canvas.getContext("2d");

const wsStatus = document.getElementById("ws-status");
const faceStatus = document.getElementById("face-status");

const confidenceText = document.getElementById("confidence");
const frameNumberText = document.getElementById("frame-number");

const roiX = document.getElementById("roi-x");
const roiY = document.getElementById("roi-y");
const roiWidth = document.getElementById("roi-width");
const roiHeight = document.getElementById("roi-height");

const startBtn = document.getElementById("start-btn");
const stopBtn = document.getElementById("stop-btn");

let stream = null;
let intervalId = null;


// websocket connection
const ws = new WebSocket("ws://localhost:8000/ws/video");

ws.onopen = () => {
    console.log("WebSocket connected");

    wsStatus.innerText = "Connected";
    wsStatus.classList.remove("disconnected");
    wsStatus.classList.add("connected");
};

ws.onclose = () => {
    console.log("WebSocket closed");

    wsStatus.innerText = "Disconnected";
    wsStatus.classList.remove("connected");
    wsStatus.classList.add("disconnected");
};

ws.onerror = (err) => {
    console.error("WebSocket Error:", err);
};

ws.onmessage = (event) => {

    const data = JSON.parse(event.data);

    console.log(data);

    if (data.frame) {
        output.src =
            "data:image/jpeg;base64," + data.frame;
    }

    if (data.face_detected) {

        faceStatus.innerText = "Face Detected";
        faceStatus.classList.remove("noface");
        faceStatus.classList.add("face");

        confidenceText.innerText =
            data.roi.confidence;

        roiX.innerText = data.roi.x;
        roiY.innerText = data.roi.y;
        roiWidth.innerText = data.roi.width;
        roiHeight.innerText = data.roi.height;

    } else {

        faceStatus.innerText = "No Face";
        faceStatus.classList.remove("face");
        faceStatus.classList.add("noface");

        confidenceText.innerText = 0;

        roiX.innerText = 0;
        roiY.innerText = 0;
        roiWidth.innerText = 0;
        roiHeight.innerText = 0;
    }

    frameNumberText.innerText =
        data.frame_number || 0;
};


// START CAMERA
startBtn.addEventListener("click", async () => {

    try {

        stream = await navigator.mediaDevices.getUserMedia({
            video: true
        });

        video.srcObject = stream;

        intervalId = setInterval(() => {

            if (ws.readyState !== WebSocket.OPEN) {
                return;
            }

            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;

            ctx.drawImage(
                video,
                0,
                0,
                canvas.width,
                canvas.height
            );

            const base64Frame = canvas
                .toDataURL("image/jpeg", 0.7)
                .split(",")[1];

            ws.send(JSON.stringify({
                frame: base64Frame
            }));

        }, 300);

    } catch (err) {

        console.error("Camera access error:", err);

        alert(
            "Unable to access webcam."
        );
    }
});


// STOP CAMERA
stopBtn.addEventListener("click", () => {

    if (intervalId) {
        clearInterval(intervalId);
    }

    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }

    video.srcObject = null;

    console.log("Camera stopped");
});