"""End-to-end rendering, with the tile and Overpass servers stubbed out.

This is the pipeline the frontend's POST body feeds into, so it doubles as a
check that `buildPayload`'s wire format is still understood.
"""

import zipfile

from PIL import Image

from modules import get_map
from modules import render_maps as render_module

SELECTION = {
    "Northwest": [49.29878484646142, 7.8759940704995755],
    "SouthEast": [49.253568734818565, 7.975131646663512],
}

BASE_CONFIG = {
    "tileLayer": "https://tile.example/{z}/{x}/{y}.png",
    "width": 288,
    "height": 201,
    "scale": 25000,
    "zoom": 13,
    "autoZoom": False,
    "upscale": False,
    "overview": False,
    "pdf": True,
    "slope": False,
}


def payload(*, coordinates=None, markers=None, **config):
    return {
        "coordinates_list": [SELECTION] if coordinates is None else coordinates,
        "markerList": markers or [],
        "config": {**BASE_CONFIG, **config},
    }


def test_single_selection_renders_a_pdf(render):
    result = render(payload(pdf=True))

    assert result.name == "MyMap.pdf"
    assert result.path.read_bytes().startswith(b"%PDF")
    assert (result.tmpdir / "Map1.png").exists()
    assert result.messages[0] == "Receiving coordinates..."
    assert result.messages[-1] == "Maps ready! Starting download..."


def test_single_selection_as_png_returns_the_image_itself(render):
    result = render(payload(pdf=False))

    assert result.name == "Map1.png"
    assert Image.open(result.path).size[0] > 0


def test_several_selections_as_png_are_bundled_into_a_zip(render):
    result = render(payload(coordinates=[SELECTION, SELECTION], pdf=False))

    assert result.name == "MyMap.zip"
    with zipfile.ZipFile(result.path) as archive:
        assert sorted(archive.namelist()) == ["Map1.png", "Map2.png"]


def test_more_than_two_selections_force_an_overview_map(render):
    result = render(payload(coordinates=[SELECTION] * 3, pdf=False))

    assert "Loading Overview Map..." in result.messages
    assert (result.tmpdir / "OverviewMap.png").exists()


def test_progress_is_reported_for_every_selection(render):
    result = render(payload(coordinates=[SELECTION, SELECTION], pdf=False))

    assert "Loading Map 1/2..." in result.messages
    assert "Loading Map 2/2..." in result.messages


def test_autozoom_replaces_the_configured_zoom(render, monkeypatch):
    seen = []
    original = render_module.getMap

    def spy(index, coordinates, markers, style, zoom, tmpdir, slope=False):
        seen.append(zoom)
        return original(index, coordinates, markers, style, zoom, tmpdir, slope=slope)

    monkeypatch.setattr(render_module, "getMap", spy)

    render(payload(autoZoom=True, zoom=3))

    assert seen == [get_map.calculateAutoZoom(SELECTION)]
    assert seen != [3], "the configured zoom must be ignored while AutoZoom is on"


def test_configured_zoom_is_used_when_autozoom_is_off(render, monkeypatch):
    seen = []
    original = render_module.getMap
    monkeypatch.setattr(
        render_module,
        "getMap",
        lambda *args, **kwargs: (seen.append(args[4]), original(*args, **kwargs))[1],
    )

    render(payload(autoZoom=False, zoom=13))

    assert seen == [13]


def test_slope_overlay_is_only_fetched_when_requested(render, tile_server):
    render(payload(slope=False, pdf=False))
    assert not any("europe-slope" in url for url in tile_server)

    tile_server.clear()
    render(payload(slope=True, pdf=False))
    assert any("europe-slope" in url for url in tile_server), (
        "slope tiles come from get_map"
    )


def test_markers_inside_the_selection_are_drawn(render, monkeypatch):
    drawn = {}
    original = get_map.draw_icons

    def spy(image, coordinates, tile_size, symbol="firepit"):
        if symbol == "marker":
            drawn["markers"] = get_map.get_markers(coordinates)
        return original(image, coordinates, tile_size, symbol=symbol)

    monkeypatch.setattr(get_map, "draw_icons", spy)

    inside = {"lat": 49.27, "lng": 7.92}
    outside = {"lat": 10.0, "lng": 10.0}
    render(payload(markers=[inside, outside], pdf=False))

    assert drawn["markers"] == [(inside["lat"], inside["lng"])]


def test_the_tile_layer_from_the_payload_is_the_one_downloaded(render, tile_server):
    render(payload(tileLayer="https://custom.example/{z}/{x}/{y}.png", pdf=False))

    assert tile_server and all(
        url.startswith("https://custom.example/") for url in tile_server
    )
