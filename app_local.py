import os
import cv2
from flask import Flask, jsonify, request, render_template_string
from Guiones.NoraCore.nora_brain import NoraBrain
from Guiones.NoraCore.nora_vision import NoraVision
from Guiones.NoraCore.nora_network import NoraNetwork
from io import BytesIO

app = Flask(__name__)

# Instancias del Core
brain = NoraBrain()
vision = NoraVision()
net = NoraNetwork()

# Flag de Modo Admin
MODO_ADMIN = False

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Nora - Panel Local</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #121212; color: white; text-align: center; }
        .container { margin-top: 50px; }
        .card { background: #1e1e1e; padding: 20px; border-radius: 15px; display: inline-block; min-width: 300px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        button { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 10px; }
        button:hover { background: #0056b3; }
        .status { color: #00ff00; font-weight: bold; }
        .admin-on { color: #ff0000; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧠 Nora Nucleo V12 - Panel Local</h1>
        <div class="card">
            <p>Estado: <span class="status">Online</span></p>
            <p>Modo Admin: <span id="admin-status">Desactivado</span></p>
            <button onclick="scanFace()">📸 Escanear Rostro (Login)</button>
            <button onclick="scanNetwork()">🌐 Escanear Red</button>
            <button onclick="speak()">🔊 Probar Voz</button>
        </div>
        <div id="results" style="margin-top: 20px; color: #aaa;"></div>
    </div>

    <script>
        async function scanFace() {
            document.getElementById('results').innerText = "Capturando cámara...";
            const res = await fetch('/api/camera');
            const data = await res.json();
            document.getElementById('results').innerText = JSON.stringify(data);
            if(data.status === 'success') {
                document.getElementById('admin-status').innerText = "ACTIVADO (Javi)";
                document.getElementById('admin-status').className = "admin-on";
            }
        }
        async function scanNetwork() {
            document.getElementById('results').innerText = "Escaneando dispositivos...";
            const res = await fetch('/api/network/scan');
            const data = await res.json();
            document.getElementById('results').innerText = JSON.stringify(data, null, 2);
        }
        function speak() {
            fetch('/api/speak', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({text: "Hola Javi, el sistema está operativo."})
            });
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/camera")
def camera_api():
    global MODO_ADMIN
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        return jsonify({"status": "error", "message": "No se pudo acceder a la cámara"}), 500
        
    _, buffer = cv2.imencode('.jpg', frame)
    img_bytesio = BytesIO(buffer)
    
    resultado = vision.analizar_rostro(img_bytesio)
    if resultado.get("status") == "success":
        MODO_ADMIN = True
        
    return jsonify(resultado)

@app.route("/api/network/scan")
def network_scan():
    if not MODO_ADMIN:
        return jsonify({"status": "denied", "message": "Debes autenticarte primero."}), 403
    dispositivos = net.buscar_dispositivos()
    return jsonify(dispositivos)

@app.route("/api/speak", methods=["POST"])
def speak_api():
    text = request.json.get("text", "")
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        return jsonify({"status": "ok"})
    except ImportError:
        return jsonify({"status": "error", "message": "pyttsx3 no instalado"}), 500

if __name__ == "__main__":
    print("🚀 Nora Local Server iniciado en http://localhost:5050")
    app.run(host="0.0.0.0", port=5050)
