"""UI components and page structure for the MapMaker FastHTML application.

The configuration panel is deliberately built out of native form controls so
that every piece of *state* it holds lives in the DOM: which output format is
selected, which orientation, whether the panel is open at all. That lets CSS
handle the presentation (the sliding pills, the blurred-out zoom row, opening
and closing the panel) and leaves JavaScript with only the parts that genuinely
need it -- talking to Leaflet.
"""

import json

from fasthtml.common import *

from . import config as cfg

SETTINGS_ID = "mapmaker-settings"


def headers():
    """Everything that belongs in ``<head>``, in load order."""
    return (
        Link(rel="icon", type="image/png", sizes="512x512", href=cfg.FAVICON),
        Link(rel="stylesheet", href=cfg.LEAFLET_CSS),
        Link(rel="stylesheet", href=cfg.LEAFLET_DRAW_CSS),
        Link(rel="stylesheet", href=cfg.LEAFLET_GEOCODER_CSS),
        Link(rel="stylesheet", href=cfg.LOCAL_CSS),
        Script(src=cfg.LEAFLET_JS),
        Script(src=cfg.LEAFLET_DRAW_JS),
        Script(src=cfg.LEAFLET_GPX_JS),
        Script(src=cfg.LEAFLET_GEOCODER_JS),
        Script(src=cfg.SSE_JS),
    )


def page():
    """The whole document body, as a FastHTML tuple."""
    return (
        Title("MapMaker fasthtml"),
        settings_json(),
        Div(id="map"),
        # `download-button` posts through JS; the other two are pure CSS/HTML:
        # a label opens the panel via a hidden checkbox, another one opens the
        # file picker via `for=`.
        Button("Download", id="download-button", cls="control-btn"),
        Label(
            "Configure", fr="configure-toggle", id="configure-button", cls="control-btn"
        ),
        Label("GPX", fr="gpxFileInput", id="gpxButton", cls="control-btn"),
        Input(type="file", id="gpxFileInput", accept=".gpx", cls="visually-hidden"),
        Input(type="checkbox", id="configure-toggle", cls="visually-hidden"),
        configuration_form(),
        log_panel(),
        Script(src=cfg.LOCAL_JS, type="module"),
    )


def settings_json():
    """Hand the browser its configuration as inert JSON rather than inline JS.

    ``<`` is escaped so no attribution string can close the ``<script>`` early.
    """
    payload = json.dumps(cfg.browser_settings()).replace("<", "\\u003c")
    return Script(payload, type="application/json", id=SETTINGS_ID)


def log_panel():
    """Progress log, appended to by the server over SSE."""
    return Div(
        hx_ext="sse",
        sse_connect="/send-message",
        hx_swap="beforeend",
        sse_swap="message",
        id="log",
    )


def configuration_form():
    """The settings panel; shown while ``#configure-toggle`` is checked."""
    return Div(
        H3("Edit Configuration"),
        Label("Scale 1:", fr="scale"),
        Input(type="number", id="scale", value=str(cfg.DEFAULT_CONFIG["scale"])),
        Br(),
        Label("AutoZoom:", fr="AutoZoom"),
        Input(type="checkbox", id="AutoZoom", checked=cfg.DEFAULT_CONFIG["autoZoom"]),
        Br(),
        Label("Zoom Level:", fr="zoom", id="zoomLabel"),
        Input(type="number", id="zoom", value=str(cfg.DEFAULT_CONFIG["zoom"])),
        Br(),
        Button("Show Zoom Level on map", type="button", id="showZoomLevel"),
        Br(),
        pill_toggle(
            "format",
            "btn",
            ("leftButton", "single PNGs"),
            ("rightButton", "bundled PDF"),
            checked_right=cfg.DEFAULT_CONFIG["pdf"],
        ),
        Br(),
        Label("Orientation:"),
        pill_toggle(
            "orientation",
            "orientationBtn",
            ("portraitButton", "Portrait"),
            ("landscapeButton", "Landscape"),
            checked_right=cfg.DEFAULT_CONFIG["orientation"] == "landscape",
            cls="orientation-box",
        ),
        id="configuration-form",
    )


def pill_toggle(name, pill_id, left, right, checked_right, cls=""):
    """A two-option switch: a radio pair with a pill that slides behind them.

    The pill is positioned purely from `:checked` in CSS, so the selection is
    readable straight off the DOM and survives without any JavaScript.
    """

    def option(opt_id, text, checked):
        return (
            Input(
                type="radio",
                name=name,
                id=opt_id,
                cls="toggle-input",
                checked=checked,
            ),
            Label(text, fr=opt_id, cls="toggle-btn"),
        )

    return Div(
        Div(id=pill_id, cls="toggle-pill"),
        *option(left[0], left[1], not checked_right),
        *option(right[0], right[1], checked_right),
        cls=f"button-box {cls}".strip(),
    )
