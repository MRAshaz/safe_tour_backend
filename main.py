from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit  # pyright: ignore[reportMissingModuleSource]
from flask_cors import CORS  # pyright: ignore[reportMissingModuleSource]
import os

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, async_mode="threading", cors_allowed_origins="*")

latest_location = {"latitude": None, "longitude": None}


@app.route("/update_location", methods=["POST"])
def update_location():
    """Receive live location updates from user"""
    data = request.json
    latest_location["latitude"] = data.get("latitude")
    latest_location["longitude"] = data.get("longitude")

    # Broadcast new location to all connected authorities
    socketio.emit("location_update", latest_location)
    return jsonify({"status": "success"})


@app.route("/sos", methods=["POST"])
def sos_alert():
    data = request.json()
    socketio.emit("sos_alert", data)
    return jsonify({"status": "SOS received"})


@app.route("/report_incident", methods=["POST"])
def report_incident():
    data = request.json

    incident = {
        "type": data.get("type"),
        "details": data.get("details"),
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude"),
        "timestamp": data.get("timestamp"),
    }

    socketio.emit("new_incident", incident)  # notify authorities in real-time
    return jsonify({"status": "incident received"})


@socketio.on("connect")
def handle_connect():
    print("Client connected")
    # Send current latest location immediately
    emit("location_update", latest_location)


@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)
