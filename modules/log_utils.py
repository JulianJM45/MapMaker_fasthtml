# log_utils.py
websocket_clients = set()

def add_websocket_client(ws):
    """Add a WebSocket client"""
    websocket_clients.add(ws)

def remove_websocket_client(ws):
    """Remove a WebSocket client"""
    websocket_clients.discard(ws)

def send_log(message):
    """Send a log message to all connected clients"""
    disconnected = set()
    for client in websocket_clients:
        try:
            import asyncio
            import json
            asyncio.create_task(client.send_text(json.dumps({"message": message})))
        except:
            disconnected.add(client)

    # Remove disconnected clients
    for client in disconnected:
        websocket_clients.discard(client)
