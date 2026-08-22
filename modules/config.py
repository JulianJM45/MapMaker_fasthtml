"""Single source of truth for MapMaker's frontend configuration.

Everything the browser needs to know -- map defaults, tile layers, icons and
legend colours -- is declared here and serialised into the page by
:func:`modules.ui.page`, so the JavaScript never re-declares it.
"""

# --- CDN assets ---------------------------------------------------------------
LEAFLET_CSS = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
LEAFLET_DRAW_CSS = "https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.css"
LEAFLET_GEOCODER_CSS = (
    "https://unpkg.com/leaflet-control-geocoder@1.13.0/dist/Control.Geocoder.css"
)

LEAFLET_JS = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
LEAFLET_DRAW_JS = "https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.js"
LEAFLET_GPX_JS = "https://cdnjs.cloudflare.com/ajax/libs/leaflet-gpx/1.5.1/gpx.min.js"
LEAFLET_GEOCODER_JS = (
    "https://unpkg.com/leaflet-control-geocoder@1.13.0/dist/Control.Geocoder.js"
)
SSE_JS = "https://unpkg.com/htmx-ext-sse@2.2.1/sse.js"

# --- Local assets -------------------------------------------------------------
LOCAL_CSS = "/static/styles.css"
LOCAL_JS = "/static/js/app.js"
FAVICON = "/icons/icon-512.png"
KOTHE_ICON = "/icons/Kothe_v1.svg"

# --- Page defaults ------------------------------------------------------------
#: Serialised into the page and used by the browser as the starting config.
#: ``width``/``height`` are the printable page size in millimetres.
DEFAULT_CONFIG = {
    "width": 288,
    "height": 201,
    "scale": 25000,
    "zoom": 14,
    "autoZoom": True,
    "upscale": False,
    "overview": False,
    "pdf": True,
    "orientation": "landscape",
}

#: Initial Leaflet viewport: ``[lat, lon], zoom``.
MAP_START = {"center": [48.149972, 11.590917], "zoom": 7}

#: Bivouac markers are only drawn from this zoom level upwards.
BIWAK_MIN_ZOOM = 10
BIWAK_ICON_SIZE = [60, 86]


def _layer(label, name, url, attribution):
    """Describe a Leaflet tile layer.

    ``label`` is what the layer control shows, ``name`` the stable identifier
    Leaflet carries on ``layer.options.name``.
    """
    return {"label": label, "name": name, "url": url, "attribution": attribution}


#: Selectable base layers, in the order they appear in the layer control.
TILE_LAYERS = [
    _layer(
        "OpenStreetMap",
        "a.tile.openstreetmap.de",
        "https://a.tile.openstreetmap.de/{z}/{x}/{y}.png",
        '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
    ),
    _layer(
        "⭐ Mapy",
        "api.mapy.com/v1/maptiles/outdoor",
        "https://api.mapy.com/v1/maptiles/outdoor/256@2x/{z}/{x}/{y}"
        "?apikey=pLSF5p9ls6uM9fXmmsMieCw0YGl6BC6AERrtMcFLgU0",
        'a href="https://api.mapy.com/copyright" target="_blank">'
        "&copy; Seznam.cz a.s. a další</a>",
    ),
    _layer(
        "OpenTopoMap",
        "a.tile.opentopomap.org",
        "https://a.tile.opentopomap.org/{z}/{x}/{y}.png",
        '&copy; <a href="https://opentopomap.org">OpenTopoMap</a> contributors',
    ),
    _layer(
        "Outdooractive",
        "t0.outdooractive.com/portal/map",
        "https://t0.outdooractive.com/portal/map/{z}/{x}/{y}.png",
        '&copy; <a href="https://www.outdooractive.com">Outdooractive</a> contributors',
    ),
    _layer(
        "Tracestrack",
        "tile.tracestrack.com/topo_en",
        "https://tile.tracestrack.com/topo_en/{z}/{x}/{y}.webp"
        "?key=0cf0393c74ee7d4cd976c5cd9f891d60",
        '&copy; <a href="https://www.tracestrack.com">Tracestrack</a> contributors',
    ),
    _layer(
        "Bergfex",
        "tiles.bergfex.at/styles/bergfex-osm",
        "https://tiles.bergfex.at/styles/bergfex-osm/{z}/{x}/{y}.jpg",
        '&copy; <a href="https://www.bergfex.at">Bergfex</a> contributors',
    ),
]

#: Overlay shown on top of the base layer; also rendered server side.
SLOPE_LAYER = {
    **_layer(
        "Slope Overlay",
        "tiles.bergfex.at/data/europe-slope-11-15",
        "https://tiles.bergfex.at/data/europe-slope-11-15/{z}/{x}/{y}.png",
        '&copy; <a href="https://www.bergfex.at">Bergfex</a> contributors',
    ),
    "opacity": 0.4,
}

#: Colour key for the slope overlay legend.
SLOPE_RANGES = [
    {"angle": "30°", "color": "rgba(255, 255, 0, 0.6)"},
    {"angle": "35°", "color": "rgba(255, 165, 0, 0.6)"},
    {"angle": "40°", "color": "rgba(255, 0, 0, 0.6)"},
    {"angle": "45°", "color": "rgba(128, 0, 128, 0.6)"},
]


def browser_settings():
    """The JSON blob handed to the frontend."""
    return {
        "defaults": DEFAULT_CONFIG,
        "mapStart": MAP_START,
        "tileLayers": TILE_LAYERS,
        "slopeLayer": SLOPE_LAYER,
        "slopeRanges": SLOPE_RANGES,
        "biwak": {
            "minZoom": BIWAK_MIN_ZOOM,
            "iconUrl": KOTHE_ICON,
            "iconSize": BIWAK_ICON_SIZE,
            "endpoint": "/api/biwaks",
        },
        "endpoints": {"render": "/send_coordinates"},
    }
