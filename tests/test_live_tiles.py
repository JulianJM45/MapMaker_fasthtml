"""Smoke test against the real tile servers.

Deselected by default -- it downloads tiles and queries Overpass. Run with:

    uv run pytest -m network
"""

import pytest

from modules import config as cfg

pytestmark = pytest.mark.network

SELECTION = {
    "Northwest": [49.29878484646142, 7.8759940704995755],
    "SouthEast": [49.253568734818565, 7.975131646663512],
}


@pytest.mark.parametrize("layer", cfg.TILE_LAYERS, ids=lambda layer: layer["name"])
def test_every_configured_tile_layer_renders(render_live, layer):
    result = render_live(
        {
            "coordinates_list": [SELECTION],
            "markerList": [],
            "config": {
                "tileLayer": layer["url"],
                "width": cfg.DEFAULT_CONFIG["width"],
                "height": cfg.DEFAULT_CONFIG["height"],
                "scale": cfg.DEFAULT_CONFIG["scale"],
                "zoom": 15,
                "autoZoom": False,
                "pdf": False,
                "slope": False,
            },
        }
    )

    assert result.path.exists()
    assert result.path.stat().st_size > 0
