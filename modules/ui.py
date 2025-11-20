# ui.py
"""UI components and page structure for MapMaker FastHTML application"""

from fasthtml.common import *
from .config import DEFAULT_CONFIG, get_local_script
import json

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
LOCAL_JS = "/static/scrips.js"

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


def header():
    head = (
        Title("MapMaker fasthtml"),
        # icon
        Link(rel="icon", type="image/png", sizes="512x512", href="/icons/icon-512.png"),

        # CSS files
        Link(rel="stylesheet", href=LEAFLET_CSS),
        Link(rel="stylesheet", href=LEAFLET_DRAW_CSS),
        Link(rel="stylesheet", href=LEAFLET_GEOCODER_CSS),
        Link(rel="stylesheet", href=LOCAL_CSS),

        # External JS files
        Script(src=LEAFLET_JS),
        Script(src=LEAFLET_DRAW_JS),
        Script(src=LEAFLET_GPX_JS),
        Script(src=LEAFLET_GEOCODER_JS),

        # local JS files
        Script(src=LOCAL_JS),
        )
    return head

def body():
    body=(
        Div(id="map"),
        Button("Download", id="download-button", cls="control-btn", ws_send='start'),
        Button("Configure", id="configure-button", cls="control-btn"),
        Button("GPX", id="gpxButton", cls="control-btn"),
        Input(type="file", id="gpxFileInput", style="display: none;"),
        configuration_form(),
        Div(id="log"),
    )
    return body






def configuration_form():
    """Create the configuration form panel"""
    return Div(
        H3("Edit Configuration"),

        # Dimensions section
        # Label("Width (mm):", For="width"),
        # Input(
        #     type="number",
        #     id="width",
        #     value=str(DEFAULT_CONFIG["width"])
        # ),
        # Br(),

        # Label("Height (mm):", For="height"),
        # Input(
        #     type="number",
        #     id="height",
        #     value=str(DEFAULT_CONFIG["height"])
        # ),
        # Br(),

        # Scale section
        Label("Scale 1:", For="scale"),
        Input(
            type="number",
            id="scale",
            value=str(DEFAULT_CONFIG["scale"])
        ),
        Br(),

        # Zoom section
        Label("AutoZoom:", For="AutoZoom"),
        Input(
            type="checkbox",
            id="AutoZoom",
            checked=DEFAULT_CONFIG["autoZoom"]
        ),
        Br(),

        Label("Zoom Level:", For="zoom", id="zoomLabel"),
        Input(
            type="number",
            id="zoom",
            value=str(DEFAULT_CONFIG["zoom"])
        ),
        Br(),

        Button("Show Zoom Level on map", id="showZoomLevel"),
        Br(),

        # Options section
        # Label("Upscale Image:", For="Upscale"),
        # Input(type="checkbox", id="Upscale"),
        # Br(),

        # Label("Create Overview Map:", For="Overview"),
        # Input(type="checkbox", id="Overview"),
        # Br(),

        # Output format toggle
        get_toggle_buttons(),

        # Orientation toggle
        get_orientation_toggle(),

        id="configuration-form",
        cls="hide"
    )

def get_toggle_buttons():
    """Create the PDF/PNG toggle button group"""
    return Div(
        Div(id="btn"),
        Button(
            "single PNGs",
            type="button",
            cls="toggle-btn",
            id="leftButton"
        ),
        Button(
            "bundled PDF",
            type="button",
            cls="toggle-btn",
            id="rightButton"
        ),
        cls="button-box"
    )

def get_orientation_toggle():
    """Create the portrait/landscape toggle button group"""
    return Div(
        Br(),
        Label("Orientation:"),
        Div(
            Div(id="orientationBtn"),
            Button(
                "Portrait",
                type="button",
                cls="toggle-btn",
                id="portraitButton"
            ),
            Button(
                "Landscape",
                type="button",
                cls="toggle-btn",
                id="landscapeButton"
            ),
            cls="button-box orientation-box"
        )
    )
