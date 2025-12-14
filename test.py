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


# data = {'coordinates_list': [[8.06821152449175, 49.33914199655545, 8.167521507734817, 49.384358108198306]], 'config': {'tileLayer': 'a.tile.openstreetmap.de', 'width': 288, 'height': 201, 'scale': 25000, 'zoom': 14, 'autoZoom': True, 'upscale': False, 'overview': False, 'pdf': False}}
# data = {
#     "coordinates_list": [coordinate_example],
#     "config": {
#         "tileLayer": tile_url[0],
#         "width": 288,
#         "height": 201,
#         "scale": 25000,
#         "zoom": 14,
#         "autoZoom": False,
#         "upscale": False,
#         "overview": False,
#         "pdf": True,
#     },
# }
coordinates_list = [{'Northwest': [47.45952049176028, 10.98186175105808], 'SouthEast': [47.41430438011742, 11.077483494303252]}]
data = {'coordinates_list': coordinates_list,
    'config': {'tileLayer': tile_url[5], 'width': 288, 'height': 201, 'scale': 25000, 'zoom': 14, 'autoZoom': True, 'pdf': True}}


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
