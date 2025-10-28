# utils.py
socketio_instance = None

def set_socketio_instance(sio):
    """
    Save the Socket.IO instance so that it can be used globally.
    """
    global socketio_instance
    socketio_instance = sio

def send_message(message):
    """
    Send a message to all connected clients via Socket.IO.
    """
    if socketio_instance is not None:
        socketio_instance.emit('py-react_communication', message)
    else:
        print("Socket.IO instance not initialized.")

