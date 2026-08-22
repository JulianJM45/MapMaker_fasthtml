"""Backend geodesy.

The browser sizes rectangles and the server re-derives their ground size from
the same constants; these tests pin both halves of that agreement.
"""

import math

import pytest

from modules.get_map import (
    ECF,
    POL_CF,
    calculateAutoZoom,
    deg2num,
    get_KPEicons,
    get_markers,
    get_xy,
    getMetersFromCoordinates,
    getZoom,
    heightFromCoordinates,
    num2deg,
    widthFromCoordinates,
)

SELECTION = {
    "Northwest": [49.29878484646142, 7.8759940704995755],
    "SouthEast": [49.253568734818565, 7.975131646663512],
}


def test_earth_constants_match_the_frontend():
    """`static/js/geo.js` hard-codes the same two numbers."""
    assert POL_CF == 40007863
    assert ECF == 40075016.686


def test_meters_from_coordinates_measures_a_known_box():
    north, west = SELECTION["Northwest"]
    south, east = SELECTION["SouthEast"]

    width, height = getMetersFromCoordinates(north, south, east, west)

    assert width == pytest.approx(7200, rel=1e-3)
    assert height == pytest.approx(5025, rel=1e-3)


def test_height_and_width_helpers_agree_with_the_combined_one():
    north, west = SELECTION["Northwest"]
    south, east = SELECTION["SouthEast"]
    width, height = getMetersFromCoordinates(north, south, east, west)

    assert heightFromCoordinates(north, south) == pytest.approx(height)
    assert widthFromCoordinates(west, east, (north + south) / 2) == pytest.approx(width)


@pytest.mark.parametrize("zoom", [5, 10, 13, 15, 18])
def test_deg2num_and_num2deg_round_trip_within_one_tile(zoom):
    lat, lon = 49.276, 7.925
    x, y = deg2num(lat, lon, zoom)
    tile_lat, tile_lon = num2deg(x, y, zoom)

    # num2deg gives the tile's north-west corner, so the point sits inside it.
    next_lat, next_lon = num2deg(x + 1, y + 1, zoom)
    assert next_lon >= lon >= tile_lon
    assert tile_lat >= lat >= next_lat


def test_autozoom_grows_as_the_selection_shrinks():
    big = {"Northwest": [50.0, 7.0], "SouthEast": [49.0, 9.0]}
    small = {"Northwest": [49.30, 7.90], "SouthEast": [49.29, 7.91]}

    assert calculateAutoZoom(small) > calculateAutoZoom(big)


def test_autozoom_matches_the_selection_it_is_derived_from():
    north, west = SELECTION["Northwest"]
    south, east = SELECTION["SouthEast"]
    width, height = getMetersFromCoordinates(north, south, east, west)

    assert calculateAutoZoom(SELECTION) == getZoom(max(width, height))


def test_get_zoom_is_the_documented_log_formula():
    assert getZoom(7200) == int(math.log2(1.3 * (POL_CF + ECF) / 7200 * 2))


def test_get_xy_maps_corners_onto_the_image():
    assert get_xy(*SELECTION["Northwest"], SELECTION, 1000, 800) == (0, 0)
    assert get_xy(*SELECTION["SouthEast"], SELECTION, 1000, 800) == (1000, 800)

    mid_lat = sum(c[0] for c in SELECTION.values()) / 2
    mid_lon = sum(c[1] for c in SELECTION.values()) / 2
    x, y = get_xy(mid_lat, mid_lon, SELECTION, 1000, 800)
    assert (x, y) == (500, 400)


def test_markers_are_filtered_to_the_selection(monkeypatch):
    from modules import get_map

    monkeypatch.setattr(
        get_map, "markerList", [{"lat": 49.27, "lng": 7.92}, {"lat": 10.0, "lng": 10.0}]
    )

    assert get_markers(SELECTION) == [(49.27, 7.92)]


def test_bivouacs_are_filtered_to_the_selection():
    world = {"Northwest": [90.0, -180.0], "SouthEast": [-90.0, 180.0]}
    from modules.get_map import BIWAKS

    assert get_KPEicons(world) == [tuple(point) for point in BIWAKS]
    assert get_KPEicons(SELECTION) == []
