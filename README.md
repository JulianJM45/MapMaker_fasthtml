# MapMaker

A web-based map generation application built with FastHTML that allows users to draw regions on an interactive map and generate high-quality printable maps in PDF or PNG format.

## Features

- **Interactive Map Interface** - Full-screen Leaflet map with multiple tile layer options
- **Region Selection** - Draw rectangular regions to define map boundaries
- **GPX Import** - Upload hiking/cycling tracks to visualize on the map
- **Geocoding Search** - Find locations by address
- **Multiple Map Styles** - Choose from OpenStreetMap, OpenTopoMap, Outdooractive, Tracestrack, Mapy.cz, and Bergfex
- **Slope Overlay** - Toggle terrain gradient visualization for outdoor activities
- **Firepit Markers** - Automatically queries Overpass API to display firepit locations
- **Configurable Output** - Adjust scale, zoom level, orientation, and output format
- **Real-time Progress** - Server-Sent Events stream progress updates during map generation

## Tech Stack

**Backend:**
- FastHTML (Python web framework)
- Uvicorn (ASGI server)
- Pillow & img2pdf (image processing)
- Overpass API (geographic features)

**Frontend:**
- Leaflet.js (map visualization)
- Leaflet-Draw (region selection)
- HTMX with SSE (real-time updates)

## Installation

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd MapMaker/fasthtml

# Install dependencies with uv
uv sync

# Or with pip
pip install -e .
```

### Running the Application

```bash
# Development mode
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or directly
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

The application will be available at `http://localhost:8000`

## Docker

```bash
# Build the image
docker build -t mapmaker .

# Run the container
docker run -p 8000:8000 mapmaker
```

## Usage

1. **Navigate the Map** - Pan and zoom to your area of interest
2. **Select a Map Style** - Choose from the available tile layers in the sidebar
3. **Draw a Region** - Use the rectangle tool to select the area you want to export
4. **Configure Settings** - Adjust scale, zoom, orientation, and format options
5. **Generate Map** - Click the generate button and monitor progress in the log window
6. **Download** - Your map will be available as a PDF or PNG download

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| Scale | Map scale ratio | 1:25000 |
| Zoom | Tile detail level | 14 |
| AutoZoom | Calculate zoom from extent | Off |
| Format | PDF or PNG output | PDF |
| Orientation | Portrait or Landscape | Portrait |
| Overview | Generate overview map | Off |
| Slope | Show slope gradient overlay | Off |

## Project Structure

```
fasthtml/
├── main.py              # Application entry point
├── modules/
│   ├── ui.py            # Frontend UI components
│   ├── config.py        # Configuration and constants
│   ├── renderMaps.py    # Map rendering pipeline
│   └── get_map.py       # Tile downloading and processing
├── static/
│   ├── scrips.js        # Frontend map logic
│   └── styles.css       # Styling
└── icons/               # Overlay icons
```

## Supported Tile Servers

- **OpenStreetMap** - General purpose maps
- **OpenTopoMap** - Topographic maps with contour lines
- **Outdooractive** - Outdoor activity focused
- **Tracestrack** - Hiking trail emphasis
- **Mapy.cz** - Czech outdoor maps
- **Bergfex** - Alpine region specialist with slope data

## License

See LICENSE file for details.
