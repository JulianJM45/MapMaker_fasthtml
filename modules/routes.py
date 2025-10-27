# routes.py
"""API routes for MapMaker FastHTML application"""

def setup_routes(rt):
    """Setup all API routes for the FastHTML app"""

    @rt("/send_coordinates", methods=["POST"])
    def send_coordinates(data: dict):
        """Handle coordinate data from the map interface"""
        coordinates_list = data.get('coordinates_list', [])
        config = data.get('config', {})

        print(f'Coordinates received: {len(coordinates_list)} rectangles')
        print(f'Config received: {config}')

        # Here you would process the data (render maps, etc.)
        return {"status": "success", "message": "Coordinates received successfully"}

    @rt("/health")
    def health():
        """Simple health check endpoint"""
        return {"status": "healthy", "app": "MapMaker FastHTML"}
