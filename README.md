# FastHTML MapMaker

A modern web application for creating and downloading map tiles built with FastHTML and real-time logging capabilities.

## Features

- **Interactive Map Interface** - Built with Leaflet.js
- **Multiple Map Layers** - OpenStreetMap, OpenTopoMap, Outdooractive, and more
- **Rectangle Drawing Tool** - Draw custom areas for map generation
- **Real-time Logging** - WebSocket-based logging from Python to frontend
- **GPX File Support** - Load and display GPX tracks
- **Configurable Output** - Customizable scale, dimensions, and formats
- **ASGI-Powered** - Built on FastHTML's modern ASGI foundation

## Quick Start

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Run the application:**
   ```bash
   python app.py
   ```

3. **Open your browser:**
   ```
   http://localhost:5001
   ```

## Usage

1. **Draw rectangles** on the map to define areas for map generation
2. **Configure settings** using the configuration panel
3. **Load GPX files** to display tracks and waypoints
4. **Download maps** by clicking the download button
5. **Watch real-time logs** in the log panel as maps are processed

## Real-time Logging

The application features a simple real-time logging system:

```python
from modules.log_utils import send_log

# Send messages to the frontend log panel
send_log("Processing started...")
send_log("Step 1 completed")
send_log("All done!")
```

## Project Structure

```
fasthtml/
├── app.py                 # Main FastHTML application
├── modules/
│   ├── config.py         # Configuration settings
│   ├── routes.py         # API routes
│   ├── ui.py            # UI components
│   ├── log_utils.py     # Real-time logging utilities
│   ├── get_map.py       # Map processing
│   └── renderMaps.py    # Map rendering
├── static/
│   ├── enhanced_map.js  # Frontend JavaScript
│   └── styles.css       # CSS styles
└── old_files/           # Legacy Flask implementation
```

## Dependencies

- **FastHTML** - Modern Python web framework
- **Pillow** - Image processing
- **Leaflet.js** - Interactive maps
- **Leaflet.draw** - Drawing tools
- **Bootstrap** - UI components

## Development

The application uses:
- **ASGI** for asynchronous operations
- **WebSockets** for real-time logging
- **uv** for dependency management
- **Modular architecture** for easy maintenance

## License

MIT License - see LICENSE file for details.