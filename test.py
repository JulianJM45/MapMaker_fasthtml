# %%
from modules.renderMaps import render_maps

coordinate_example = [
    8.06821152449175,
    49.33914199655545,
    8.167521507734817,
    49.384358108198306,
]
tile_url = [
    "https://a.tile.openstreetmap.de/{z}/{x}/{y}.png",
    "https://a.tile.opentopomap.org/{z}/{x}/{y}.png",
    "https://t0.outdooractive.com/portal/map/{z}/{x}/{y}.png",
    "https://tile.tracestrack.com/topo_en/{z}/{x}/{y}.webp?key=0cf0393c74ee7d4cd976c5cd9f891d60",
    "https://api.mapy.com/v1/maptiles/outdoor/256@2x/{z}/{x}/{y}?apikey=pLSF5p9ls6uM9fXmmsMieCw0YGl6BC6AERrtMcFLgU0",
]


# data = {'coordinates_list': [[8.06821152449175, 49.33914199655545, 8.167521507734817, 49.384358108198306]], 'config': {'tileLayer': 'a.tile.openstreetmap.de', 'width': 288, 'height': 201, 'scale': 25000, 'zoom': 14, 'autoZoom': True, 'upscale': False, 'overview': False, 'pdf': False}}
data = {
    "coordinates_list": [coordinate_example],
    "config": {
        "tileLayer": tile_url[0],
        "width": 288,
        "height": 201,
        "scale": 25000,
        "zoom": 14,
        "autoZoom": False,
        "upscale": False,
        "overview": False,
        "pdf": True,
    },
}
data = {'coordinates_list': [{'Northwest': [49.34840125457684, 8.102150918109585], 'SouthEast': [49.303185142933984, 8.201388358013466]}], 'config': {'tileLayer': 'https://a.tile.openstreetmap.de/{z}/{x}/{y}.png', 'width': 288, 'height': 201, 'scale': 25000, 'zoom': 14, 'autoZoom': True, 'pdf': True}}
data = {'coordinates_list': [{'Northwest': [49.37714603607883, 8.066416361069068], 'SouthEast': [49.33192992443597, 8.165711782241482]}, {'Northwest': [49.34521232737785, 8.132624025865104], 'SouthEast': [49.29999621573499, 8.231855039076306]}], 'config': {'tileLayer': 'https://a.tile.openstreetmap.de/{z}/{x}/{y}.png', 'width': 288, 'height': 201, 'scale': 25000, 'zoom': 14, 'autoZoom': True, 'pdf': False}}
# print(data)


file_path, file_name = render_maps(data)
# print("hello world")
