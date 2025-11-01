from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit  # pyright: ignore[reportMissingModuleSource]
from flask_cors import CORS  # pyright: ignore[reportMissingModuleSource]

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

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

@socketio.on("connect")
def handle_connect():
    print("Client connected")
    # Send current latest location immediately
    emit("location_update", latest_location)

@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
