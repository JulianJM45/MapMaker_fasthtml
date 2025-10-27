# config.py
"""Configuration file for MapMaker FastHTML application"""

from fasthtml.common import Link, Script

# External CSS dependencies
LEAFLET_CSS = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
LEAFLET_DRAW_CSS = "https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.css"
LEAFLET_GEOCODER_CSS = "https://unpkg.com/leaflet-control-geocoder@1.13.0/dist/Control.Geocoder.css"

# External JS dependencies
LEAFLET_JS = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
LEAFLET_DRAW_JS = "https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.js"
LEAFLET_GPX_JS = "https://cdnjs.cloudflare.com/ajax/libs/leaflet-gpx/1.5.1/gpx.min.js"
LEAFLET_GEOCODER_JS = "https://unpkg.com/leaflet-control-geocoder@1.13.0/dist/Control.Geocoder.js"

# Local static files
LOCAL_CSS = "/static/styles.css"
LOCAL_JS = "/static/enhanced_map.js"
# LOCAL_JS = "/static/scripts.js"

def get_app_headers():
    """Return all CSS and JS headers for the FastHTML app"""
    return (
        # CSS files first
        Link(rel="stylesheet", href=LEAFLET_CSS),
        Link(rel="stylesheet", href=LEAFLET_DRAW_CSS),
        Link(rel="stylesheet", href=LEAFLET_GEOCODER_CSS),
        Link(rel="stylesheet", href=LOCAL_CSS),

        # External JS files only
        Script(src=LEAFLET_JS),
        Script(src=LEAFLET_DRAW_JS),
        Script(src=LEAFLET_GPX_JS),
        Script(src=LEAFLET_GEOCODER_JS),
    )

def get_local_script():
    """Return the local JavaScript file"""
    return Script(src=LOCAL_JS)

# Default configuration values
DEFAULT_CONFIG = {
    "width": 288,
    "height": 201,
    "scale": 25000,
    "zoom": 14,
    "autoZoom": True,
    "upscale": False,
    "overview": False,
    "pdf": True,
    "orientation": "landscape"
}
