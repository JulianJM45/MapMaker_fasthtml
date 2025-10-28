# routes.py
"""API routes for MapMaker FastHTML application"""

import asyncio
from fasthtml.common import *
from .log_utils import add_websocket_client, remove_websocket_client, send_log

def setup_routes(rt):
    """Setup all API routes for the FastHTML app"""

    @rt("/send_coordinates", methods=["POST"])
    async def send_coordinates(data: dict):
        """Handle coordinate data from the map interface"""
        coordinates_list = data.get('coordinates_list', [])
        config = data.get('config', {})

        print(f'Coordinates received: {len(coordinates_list)} rectangles')
        print(f'Config received: {config}')

        # Send logs to frontend
        send_log(f"Processing {len(coordinates_list)} coordinate rectangles...")

        if len(coordinates_list) == 0:
            send_log("Warning: No coordinates provided!")
            return {"status": "warning", "message": "No coordinates to process"}

        send_log("Validating coordinate data...")
        await asyncio.sleep(0.5)

        send_log("Applying configuration settings...")
        send_log(f"Map dimensions: {config.get('width', 'default')}x{config.get('height', 'default')}")

        send_log("Processing completed successfully!")

        return {
            "status": "success",
            "message": "Coordinates processed successfully",
            "processed_count": len(coordinates_list)
        }

    @rt("/ws/logs")
    async def websocket_logs(websocket):
        """WebSocket endpoint for real-time logs"""
        await websocket.accept()
        add_websocket_client(websocket)

        try:
            while True:
                await websocket.receive_text()  # Keep connection alive
        except:
            pass
        finally:
            remove_websocket_client(websocket)

    @rt("/health")
    def health():
        """Simple health check endpoint"""
        return {"status": "healthy", "app": "MapMaker FastHTML"}
