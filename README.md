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
- ES modules; no build step and no framework

The configuration panel is plain HTML: its state lives in native form controls
and CSS drives the presentation, so JavaScript is only used where Leaflet needs
it. Defaults, tile layers and legend colours are declared once in
`modules/config.py` and serialised into the page.

## Installation

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Setup

```bash
# Clone the repository
git clone https://github.com/JulianJM45/MapMaker_fasthtml.git
cd MapMaker_fasthtml

# Install dependencies with uv
uv sync
```

### Running the Application
Quick test
```bash
uv run main.py
```

Development mode
```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at `http://localhost:8000`

## Tests

```bash
uv sync                # installs the dev group (pytest)
uv run pytest          # backend, page rendering, stylesheet and wire-format tests
npm test               # frontend unit tests (node:test, no dependencies)
```

Both suites are hermetic -- tile servers and Overpass are stubbed out. Two
groups are deselected by default:

```bash
uv run pytest -m network    # smoke test against the real tile servers

uv sync --group e2e && uv run playwright install chromium
uv run pytest -m e2e        # drives the app in a headless browser
```

| Suite | What it covers |
|-------|----------------|
| `tests/js/` | Rectangle geometry, configuration reading and the request body. Asserted **bit-for-bit** against reference implementations of the pre-refactor script in `tests/js/legacy.mjs`. |
| `tests/test_page.py` | Every element id and default value the CSS and JS depend on. |
| `tests/test_styles.py` | The CSS rules that took over from JavaScript (panel toggle, sliding pills, AutoZoom blur). |
| `tests/test_contract.py` | Runs the real frontend modules under Node and feeds their payload into the Python renderer. |
| `tests/test_render_maps.py` | The full render pipeline (PDF, ZIP, PNG, overview, slope, markers) against a stubbed tile server. |
| `tests/test_geometry.py` | The backend geodesy the frontend has to agree with. |
| `tests/e2e/` | The real thing in Chromium: drawing, toggling, downloading. |

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
├── main.py               # Application entry point and routes
├── modules/
│   ├── config.py         # Single source of truth for the frontend config
│   ├── ui.py             # Page structure and components
│   ├── responses.py      # Self-cleaning file response
│   ├── render_maps.py    # Map rendering pipeline
│   └── get_map.py        # Tile downloading and processing
├── static/
│   ├── styles.css        # Styling; also drives the panel's interactions
│   └── js/
│       ├── app.js        # Entry point: wires Leaflet to the page
│       ├── geo.js        # Rectangle geometry (pure)
│       ├── layers.js     # Tile layers, slope legend, bivouac markers
│       ├── settings.js   # Reads the injected config and the live form
│       └── download.js   # Request body and the download round-trip
├── tests/                # Python suites, `js/` unit tests, `e2e/` browser tests
├── data/                 # Bivouac coordinates
└── icons/                # Overlay icons
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
