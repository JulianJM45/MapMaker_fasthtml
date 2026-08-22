"""Browser tests for the behaviour that moved from JavaScript into CSS.

Everything asserted here used to be implemented imperatively in `scrips.js`.
The point of these tests is that the *observable* result is unchanged.
"""

import json

import pytest

from modules import config as cfg

pytestmark = pytest.mark.e2e


def computed(page, selector, prop):
    return page.eval_on_selector(selector, f"e => getComputedStyle(e)[{prop!r}]")


# --- map ----------------------------------------------------------------------


def test_the_map_and_its_controls_are_built(app_page):
    assert app_page.locator(".leaflet-container").count() == 1
    assert app_page.locator(".leaflet-control-layers").count() == 1, "layer switcher"
    assert app_page.locator(".leaflet-draw").count() == 1, "draw toolbar"
    assert app_page.locator(".leaflet-control-geocoder").count() == 1, "address search"


def test_the_map_opens_on_the_configured_view(app_page):
    center = app_page.evaluate("[__map.getCenter().lat, __map.getCenter().lng]")

    assert center == pytest.approx(cfg.MAP_START["center"])
    assert app_page.evaluate("__map.getZoom()") == cfg.MAP_START["zoom"]


def test_every_configured_base_layer_is_offered(app_page):
    app_page.click(".leaflet-control-layers")
    labels = app_page.locator(".leaflet-control-layers-base label").all_inner_texts()

    assert [label.strip() for label in labels] == [
        layer["label"] for layer in cfg.TILE_LAYERS
    ]


# --- configuration panel (was: setupConfigurationToggle) ----------------------


def test_the_panel_opens_and_closes_without_javascript(app_page):
    panel = app_page.locator("#configuration-form")
    assert not panel.is_visible(), "starts closed"

    app_page.click("#configure-button")
    assert panel.is_visible()

    app_page.click("#configure-button")
    assert not panel.is_visible()


# --- pill toggles (was: class ToggleButton) ----------------------------------


@pytest.mark.parametrize(
    ("pill", "left", "right", "left_offset", "right_offset"),
    [
        ("#btn", "leftButton", "rightButton", "0px", "150px"),
        ("#orientationBtn", "portraitButton", "landscapeButton", "0px", "125px"),
    ],
)
def test_the_pill_slides_to_the_selected_option(
    app_page, pill, left, right, left_offset, right_offset
):
    app_page.click("#configure-button")

    # The right-hand option (PDF / landscape) is the default, as before.
    assert app_page.is_checked(f"#{right}")
    assert computed(app_page, pill, "left") == right_offset

    app_page.click(f"label[for={left}]")
    app_page.wait_for_timeout(700)  # the pill transition
    assert app_page.is_checked(f"#{left}")
    assert computed(app_page, pill, "left") == left_offset

    app_page.click(f"label[for={right}]")
    app_page.wait_for_timeout(700)
    assert computed(app_page, pill, "left") == right_offset


def test_changing_the_scale_no_longer_resets_the_toggles(app_page):
    """The old `updateConfiguration` rebuilt the config and lost the pills."""
    app_page.click("#configure-button")
    app_page.click("label[for=leftButton]")
    app_page.click("label[for=portraitButton]")

    app_page.fill("#scale", "10000")

    assert app_page.is_checked("#leftButton"), "still single PNGs"
    assert app_page.is_checked("#portraitButton"), "still portrait"


# --- AutoZoom (was: the disabled/blur listener) ------------------------------


def test_autozoom_blurs_and_disables_the_manual_zoom_row(app_page):
    app_page.click("#configure-button")
    assert app_page.is_checked("#AutoZoom"), "on by default"

    for selector in ["#zoom", "#zoomLabel", "#showZoomLevel"]:
        assert computed(app_page, selector, "filter") == "blur(2px)"
        assert computed(app_page, selector, "pointerEvents") == "none"

    app_page.uncheck("#AutoZoom")
    for selector in ["#zoom", "#zoomLabel", "#showZoomLevel"]:
        assert computed(app_page, selector, "filter") == "none"
        assert computed(app_page, selector, "pointerEvents") == "auto"


def test_show_zoom_level_moves_the_map(app_page):
    app_page.click("#configure-button")
    app_page.uncheck("#AutoZoom")
    app_page.fill("#zoom", "12")

    app_page.click("#showZoomLevel")

    assert app_page.evaluate("__map.getZoom()") == 12


# --- slope overlay -----------------------------------------------------------


def test_the_slope_legend_follows_the_overlay(app_page):
    legend = app_page.locator(".slope-legend").first
    assert legend.locator(".slope-legend-item").count() == len(cfg.SLOPE_RANGES)
    assert not legend.is_visible(), "hidden until the overlay is switched on"

    app_page.click(".leaflet-control-layers")
    app_page.check(".leaflet-control-layers-overlays input")
    assert legend.is_visible()
    assert legend.inner_text().split() == [r["angle"] for r in cfg.SLOPE_RANGES]

    app_page.uncheck(".leaflet-control-layers-overlays input")
    assert not legend.is_visible()


# --- bivouac markers ---------------------------------------------------------


def test_bivouacs_appear_only_past_the_configured_zoom(app_page):
    kothe = f'img[src*="{cfg.KOTHE_ICON.rsplit("/", 1)[-1]}"]'
    assert app_page.locator(kothe).count() == 0, "hidden at the starting zoom"

    app_page.evaluate(f"__map.setZoom({cfg.BIWAK_MIN_ZOOM})")
    app_page.wait_for_selector(kothe)
    assert app_page.locator(kothe).count() > 0

    app_page.evaluate(f"__map.setZoom({cfg.BIWAK_MIN_ZOOM - 1})")
    app_page.wait_for_function(f"document.querySelectorAll({kothe!r}).length === 0")


# --- drawing and downloading --------------------------------------------------


DRAW_RECTANGLE = """
([sw, ne]) => {
  const rectangle = L.rectangle(L.latLngBounds(L.latLng(...sw), L.latLng(...ne)));
  __map.fire("draw:created", { layer: rectangle, layerType: "rectangle" });
  const b = rectangle.getBounds();
  return { north: b.getNorth(), south: b.getSouth(), east: b.getEast(), west: b.getWest() };
}
"""

# What leaflet-draw's delete tool does: drop the layer from the editable group.
DELETE_RECTANGLES = """
() =>
  __map.eachLayer((layer) => {
    if (layer instanceof L.Rectangle) {
      Object.values(layer._eventParents ?? {}).forEach((group) => group.removeLayer?.(layer));
    }
  });
"""

DROP_MARKER = """
(latlng) => {
  const marker = L.marker(L.latLng(...latlng));
  __map.fire("draw:created", { layer: marker, layerType: "marker" });
}
"""


def test_a_drawn_rectangle_snaps_to_one_page_at_the_current_scale(app_page):
    bounds = app_page.evaluate(DRAW_RECTANGLE, [[48.10, 11.50], [48.20, 11.70]])

    from modules.get_map import getMetersFromCoordinates

    width, height = getMetersFromCoordinates(
        bounds["north"], bounds["south"], bounds["east"], bounds["west"]
    )
    scale = cfg.DEFAULT_CONFIG["scale"]
    assert width == pytest.approx(cfg.DEFAULT_CONFIG["width"] * scale / 1000, rel=1e-6)
    assert height == pytest.approx(
        cfg.DEFAULT_CONFIG["height"] * scale / 1000, rel=1e-6
    )


def test_portrait_swaps_the_page_dimensions(app_page):
    app_page.click("#configure-button")
    app_page.click("label[for=portraitButton]")

    bounds = app_page.evaluate(DRAW_RECTANGLE, [[48.10, 11.50], [48.20, 11.70]])

    from modules.get_map import getMetersFromCoordinates

    width, height = getMetersFromCoordinates(
        bounds["north"], bounds["south"], bounds["east"], bounds["west"]
    )
    assert height > width, "a portrait page is taller than it is wide"


def test_download_posts_the_selection_and_saves_the_file(app_page):
    posted = {}

    def fulfill(route):
        posted.update(route.request.post_data_json)
        route.fulfill(
            status=200,
            headers={"Content-Disposition": 'attachment; filename="MyMap.pdf"'},
            content_type="application/pdf",
            body=b"%PDF-1.4 stub",
        )

    app_page.route("**/send_coordinates", fulfill)
    app_page.evaluate(DRAW_RECTANGLE, [[48.10, 11.50], [48.20, 11.70]])
    app_page.evaluate(DROP_MARKER, [48.15, 11.60])

    with app_page.expect_download() as download:
        app_page.click("#download-button")

    assert download.value.suggested_filename == "MyMap.pdf"
    assert app_page.locator("#log").inner_text() == "Map downloaded successfully!"

    assert len(posted["coordinates_list"]) == 1
    assert posted["markerList"] == [{"lat": 48.15, "lng": 11.60}]
    assert posted["config"]["tileLayer"] == cfg.TILE_LAYERS[0]["url"]
    assert posted["config"]["pdf"] is True
    assert posted["config"]["slope"] is False
    assert posted["config"]["scale"] == cfg.DEFAULT_CONFIG["scale"]


def test_download_reports_a_failing_render_in_the_log(app_page):
    app_page.route(
        "**/send_coordinates", lambda route: route.fulfill(status=500, body="boom")
    )
    app_page.evaluate(DRAW_RECTANGLE, [[48.10, 11.50], [48.20, 11.70]])

    app_page.click("#download-button")
    app_page.wait_for_function(
        "document.getElementById('log').innerText.includes('An error occurred')"
    )

    # The failure is reported, but the log drops back behind the map either way.
    assert computed(app_page, "#log", "zIndex") == "0"
    app_page.console_errors.clear()  # the handler logs the failure on purpose


def test_download_closes_the_panel_and_raises_the_log(app_page):
    app_page.route(
        "**/send_coordinates",
        lambda route: route.fulfill(
            status=200,
            headers={"Content-Disposition": 'attachment; filename="MyMap.pdf"'},
            body=b"%PDF-1.4 stub",
        ),
    )
    app_page.click("#configure-button")
    assert app_page.locator("#configuration-form").is_visible()
    app_page.evaluate(DRAW_RECTANGLE, [[48.10, 11.50], [48.20, 11.70]])

    # The open panel overlaps the button (it always has), so click it directly.
    with app_page.expect_download():
        app_page.dispatch_event("#download-button", "click")

    assert not app_page.locator("#configuration-form").is_visible()


def test_a_deleted_rectangle_is_not_submitted(app_page):
    posted = {}

    app_page.route(
        "**/send_coordinates",
        lambda route: (
            posted.update(route.request.post_data_json),
            route.fulfill(
                status=200,
                headers={"Content-Disposition": 'attachment; filename="x.pdf"'},
                body=b"%PDF",
            ),
        )[1],
    )
    app_page.evaluate(DRAW_RECTANGLE, [[48.10, 11.50], [48.20, 11.70]])
    app_page.evaluate(DELETE_RECTANGLES)

    with app_page.expect_download():
        app_page.click("#download-button")

    assert posted["coordinates_list"] == []


def test_the_selected_tile_layer_is_the_one_submitted(app_page):
    posted = {}

    app_page.route(
        "**/send_coordinates",
        lambda route: (
            posted.update(route.request.post_data_json),
            route.fulfill(
                status=200,
                headers={"Content-Disposition": 'attachment; filename="x.pdf"'},
                body=b"%PDF",
            ),
        )[1],
    )

    app_page.click(".leaflet-control-layers")
    app_page.locator(".leaflet-control-layers-base input").nth(2).check()
    app_page.check(".leaflet-control-layers-overlays input")
    app_page.evaluate(DRAW_RECTANGLE, [[48.10, 11.50], [48.20, 11.70]])

    with app_page.expect_download():
        app_page.click("#download-button")

    assert posted["config"]["tileLayer"] == cfg.TILE_LAYERS[2]["url"]
    assert posted["config"]["slope"] is True, "the overlay is reported separately"


def test_the_settings_blob_is_what_the_frontend_reads(app_page):
    blob = app_page.evaluate(
        "JSON.parse(document.getElementById('mapmaker-settings').textContent)"
    )

    assert blob == json.loads(json.dumps(cfg.browser_settings()))
