# %%
import asyncio

from modules.renderMaps import render_maps

tile_url = [
    "https://a.tile.openstreetmap.de/{z}/{x}/{y}.png",
    "https://a.tile.opentopomap.org/{z}/{x}/{y}.png",
    "https://t0.outdooractive.com/portal/map/{z}/{x}/{y}.png",
    "https://tile.tracestrack.com/topo_en/{z}/{x}/{y}.webp?key=0cf0393c74ee7d4cd976c5cd9f891d60",
    "https://api.mapy.com/v1/maptiles/outdoor/256@2x/{z}/{x}/{y}?apikey=pLSF5p9ls6uM9fXmmsMieCw0YGl6BC6AERrtMcFLgU0",
    "https://tiles.bergfex.at/styles/bergfex-osm/{z}/{x}/{y}.jpg",
]


coordinates_list = [
    {
        "Northwest": [49.29878484646142, 7.8759940704995755],
        "SouthEast": [49.253568734818565, 7.975131646663512],
    }
]


data = {
    "coordinates_list": coordinates_list,
    "config": {
        "tileLayer": tile_url[4],
        "width": 288,
        "height": 201,
        "scale": 25000,
        "zoom": 15,
        "autoZoom": False,
        "pdf": False,
    },
}


# file_path, file_name = render_maps(data)
async def ws(msg):
    print(msg)


async def test_render_maps():
    file_path, file_name, tmpdir = await render_maps(data, ws)
    print(f"Generated: {file_name} at {file_path}")
    print(f"Temp directory: {tmpdir}")


# Run the async function
asyncio.run(test_render_maps())
# print("hello world")
