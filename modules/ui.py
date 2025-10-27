# ui.py
"""UI components and page structure for MapMaker FastHTML application"""

from fasthtml.common import *
from .config import DEFAULT_CONFIG, get_local_script
import json

def get_control_buttons():
    """Create the main control buttons for the map interface"""
    download_btn = Button(
        "Download",
        id="download-button",
        cls="control-btn",
    )

    configure_btn = Button(
        "Configure",
        id="configure-button",
        cls="control-btn",
    )

    gpx_btn = Button(
        "GPX",
        id="gpxButton",
        cls="control-btn",
        style="left: 10px; top: 290px; width: 60px;"
    )

    return download_btn, configure_btn, gpx_btn

def get_file_inputs():
    """Create hidden file input elements"""
    return Input(
        type="file",
        id="gpxFileInput",
        style="display: none;"
    )

def get_configuration_form():
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

def get_log_panel():
    """Create the log output panel"""
    return Div(id="log")

def get_map_container():
    """Create the main map container"""
    return Div(id="map")

def get_main_page():
    """Create the complete main page with all components"""
    # Get all components
    download_btn, configure_btn, gpx_btn = get_control_buttons()
    file_inputs = get_file_inputs()
    config_form = get_configuration_form()
    log_panel = get_log_panel()
    map_container = get_map_container()

    # Create JavaScript config initialization script
    config_script = Script(f"""
        window.DEFAULT_CONFIG = {json.dumps(DEFAULT_CONFIG)};
    """)

    # Return complete page
    return Titled(
        "MapMaker FastHTML",
        map_container,
        download_btn,
        configure_btn,
        gpx_btn,
        file_inputs,
        config_form,
        log_panel,
        config_script,
        get_local_script()
    )
