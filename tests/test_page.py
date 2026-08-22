"""The rendered page must expose everything the CSS and JS hang off."""

import json

import pytest

from modules import config as cfg
from modules import ui


def test_document_is_well_formed(page):
    """One <head> and one <body> -- the old page nested a second pair inside <main>."""
    assert len(page.by_tag("head")) == 1
    assert len(page.by_tag("body")) == 1
    assert len(page.by_tag("main")) == 0


def test_head_loads_every_asset_in_order(page):
    stylesheets = [
        link["href"] for link in page.by_tag("link") if link.get("rel") == "stylesheet"
    ]
    scripts = [s["src"] for s in page.by_tag("script") if "src" in s.attrs]

    assert stylesheets == [
        cfg.LEAFLET_CSS,
        cfg.LEAFLET_DRAW_CSS,
        cfg.LEAFLET_GEOCODER_CSS,
        cfg.LOCAL_CSS,
    ]
    for src in (
        cfg.LEAFLET_JS,
        cfg.LEAFLET_DRAW_JS,
        cfg.LEAFLET_GPX_JS,
        cfg.LEAFLET_GEOCODER_JS,
        cfg.SSE_JS,
    ):
        assert src in scripts

    icons = [link for link in page.by_tag("link") if link.get("rel") == "icon"]
    assert icons and icons[0]["href"] == cfg.FAVICON


def test_frontend_entry_point_is_a_module(page):
    entry = [s for s in page.by_tag("script") if s.get("src") == cfg.LOCAL_JS]
    assert len(entry) == 1, "the app must be loaded exactly once"
    assert entry[0].get("type") == "module"


@pytest.mark.parametrize(
    "element_id",
    [
        "map",
        "log",
        "download-button",
        "configure-button",
        "configure-toggle",
        "gpxButton",
        "gpxFileInput",
        "configuration-form",
        "scale",
        "AutoZoom",
        "zoomLabel",
        "zoom",
        "showZoomLevel",
        "btn",
        "leftButton",
        "rightButton",
        "orientationBtn",
        "portraitButton",
        "landscapeButton",
    ],
)
def test_required_element_is_present(page, element_id):
    assert element_id in page


def test_log_is_wired_to_the_sse_stream(page):
    log = page["log"]
    assert log["hx-ext"] == "sse"
    assert log["sse-connect"] == "/send-message"
    assert log["sse-swap"] == "message"
    assert log["hx-swap"] == "beforeend"


def test_configure_and_gpx_buttons_need_no_javascript(page):
    """Both are labels driving a native input, which is what removed their JS."""
    assert page["configure-button"].tag == "label"
    assert page["configure-button"]["for"] == "configure-toggle"
    assert page["configure-toggle"]["type"] == "checkbox"

    assert page["gpxButton"].tag == "label"
    assert page["gpxButton"]["for"] == "gpxFileInput"
    assert page["gpxFileInput"]["type"] == "file"


def test_configure_toggle_precedes_the_panel(page):
    """`#configure-toggle:checked ~ #configuration-form` needs this order."""
    assert page.id_order.index("configure-toggle") < page.id_order.index(
        "configuration-form"
    )


def test_panel_fields_carry_the_python_defaults(page):
    assert page["scale"]["value"] == str(cfg.DEFAULT_CONFIG["scale"])
    assert page["zoom"]["value"] == str(cfg.DEFAULT_CONFIG["zoom"])
    assert ("checked" in page["AutoZoom"].attrs) is cfg.DEFAULT_CONFIG["autoZoom"]


def test_toggles_are_radio_pairs_defaulting_to_pdf_and_landscape(page):
    for left, right, group in [
        ("leftButton", "rightButton", "format"),
        ("portraitButton", "landscapeButton", "orientation"),
    ]:
        for element_id in (left, right):
            assert page[element_id]["type"] == "radio"
            assert page[element_id]["name"] == group

    assert "checked" not in page["leftButton"].attrs, "PNG is not the default"
    assert "checked" in page["rightButton"].attrs, "PDF is the default"
    assert "checked" not in page["portraitButton"].attrs
    assert "checked" in page["landscapeButton"].attrs

    assert cfg.DEFAULT_CONFIG["pdf"] is True
    assert cfg.DEFAULT_CONFIG["orientation"] == "landscape"


def test_settings_blob_carries_the_python_configuration(page):
    settings = json.loads(page[ui.SETTINGS_ID].text)

    assert settings["defaults"] == cfg.DEFAULT_CONFIG
    assert settings["mapStart"] == cfg.MAP_START
    assert settings["tileLayers"] == cfg.TILE_LAYERS
    assert settings["slopeLayer"] == cfg.SLOPE_LAYER
    assert settings["slopeRanges"] == cfg.SLOPE_RANGES
    assert settings["biwak"]["minZoom"] == cfg.BIWAK_MIN_ZOOM
    assert settings["endpoints"]["render"] == "/send_coordinates"


def test_settings_blob_cannot_break_out_of_its_script_tag(client):
    """Attributions contain raw HTML; `<` must be escaped inside the JSON."""
    body = client.get("/").text
    blob = body.split(f'id="{ui.SETTINGS_ID}">')[1].split("</script>")[0]

    escaped = chr(92) + "u003c"  # a literal backslash-u003c in the JSON text
    assert "<" not in blob
    assert escaped in blob
    assert json.loads(blob)["tileLayers"][0]["attribution"].startswith(
        "&copy; <a href="
    )


def test_tile_layers_are_unchanged(page):
    """The exact set, order and URLs the app shipped with."""
    settings = json.loads(page[ui.SETTINGS_ID].text)

    assert [layer["label"] for layer in settings["tileLayers"]] == [
        "OpenStreetMap",
        "⭐ Mapy",
        "OpenTopoMap",
        "Outdooractive",
        "Tracestrack",
        "Bergfex",
    ]
    assert [layer["name"] for layer in settings["tileLayers"]] == [
        "a.tile.openstreetmap.de",
        "api.mapy.com/v1/maptiles/outdoor",
        "a.tile.opentopomap.org",
        "t0.outdooractive.com/portal/map",
        "tile.tracestrack.com/topo_en",
        "tiles.bergfex.at/styles/bergfex-osm",
    ]
    for layer in settings["tileLayers"] + [settings["slopeLayer"]]:
        assert "{z}" in layer["url"] and "{x}" in layer["url"] and "{y}" in layer["url"]

    assert settings["slopeLayer"]["opacity"] == 0.4
    assert [r["angle"] for r in settings["slopeRanges"]] == ["30°", "35°", "40°", "45°"]
