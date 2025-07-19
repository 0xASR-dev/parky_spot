from app import socketio



@socketio.on('connect')
def handle_connect():
    """Handle WebSocket client connection."""
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket client disconnection."""
    print("Client disconnected")
