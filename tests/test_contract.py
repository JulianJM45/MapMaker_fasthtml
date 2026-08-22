"""The contract between the browser and the server.

The frontend modules are executed with Node against the settings blob this app
actually renders, and the payload they produce is fed straight into the Python
renderer. If either side drifts, this fails.
"""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from modules import config as cfg
from modules.get_map import getMetersFromCoordinates

ROOT = Path(__file__).resolve().parent.parent
NODE = shutil.which("node")

pytestmark = pytest.mark.skipif(NODE is None, reason="node is not installed")


@pytest.fixture(scope="session")
def browser_payload(tmp_path_factory):
    """The body the real frontend modules build, straight from Node."""
    settings = tmp_path_factory.mktemp("contract") / "settings.json"
    settings.write_text(json.dumps(cfg.browser_settings()))

    result = subprocess.run(
        [NODE, "tests/build_payload.mjs", str(settings)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def test_payload_shape(browser_payload):
    assert set(browser_payload) == {"coordinates_list", "markerList", "config"}

    (selection,) = browser_payload["coordinates_list"]
    assert set(selection) == {"Northwest", "SouthEast"}
    assert selection["Northwest"][0] > selection["SouthEast"][0], "north is above south"
    assert selection["Northwest"][1] < selection["SouthEast"][1], "west is left of east"

    assert browser_payload["markerList"] == [{"lat": 49.276, "lng": 7.925}]


def test_payload_config_carries_the_python_defaults(browser_payload):
    config = browser_payload["config"]

    assert config["width"] == cfg.DEFAULT_CONFIG["width"]
    assert config["height"] == cfg.DEFAULT_CONFIG["height"]
    assert config["upscale"] == cfg.DEFAULT_CONFIG["upscale"]
    assert config["overview"] == cfg.DEFAULT_CONFIG["overview"]
    assert config["tileLayer"] == cfg.TILE_LAYERS[0]["url"]


def test_selection_is_exactly_one_page_at_the_chosen_scale(browser_payload):
    (selection,) = browser_payload["coordinates_list"]
    north, west = selection["Northwest"]
    south, east = selection["SouthEast"]
    width_meters, height_meters = getMetersFromCoordinates(north, south, east, west)

    config = browser_payload["config"]
    assert width_meters == pytest.approx(
        config["width"] * config["scale"] / 1000, rel=1e-9
    )
    assert height_meters == pytest.approx(
        config["height"] * config["scale"] / 1000, rel=1e-9
    )


def test_the_server_renders_the_browser_payload(render, browser_payload):
    result = render(browser_payload)

    assert result.name == "MyMap.pdf"
    assert result.path.read_bytes().startswith(b"%PDF")
    assert result.messages[-1] == "Maps ready! Starting download..."


def test_render_maps_reads_no_config_key_the_frontend_omits(browser_payload):
    source = (ROOT / "modules" / "render_maps.py").read_text()
    read_keys = set(re.findall(r'config\.get\(\s*"([^"]+)"', source))

    missing = read_keys - set(browser_payload["config"])
    assert not missing, f"the server reads {missing}, which the browser never sends"


def test_frontend_field_ids_exist_on_the_page(page):
    """`settings.js` looks these up by id; the page must render them."""
    fields = (ROOT / "static" / "js" / "settings.js").read_text()

    for element_id in ["scale", "zoom", "AutoZoom", "leftButton", "portraitButton"]:
        assert f'"{element_id}"' in fields, f"{element_id} dropped from FIELDS"
        assert element_id in page, f"{element_id} dropped from the page"


def test_the_settings_blob_the_page_ships_is_what_node_consumes(page, browser_payload):
    """Sanity: the blob used above is the one really rendered into the page."""
    from modules import ui

    assert json.loads(page[ui.SETTINGS_ID].text) == cfg.browser_settings()
