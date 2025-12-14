import math
import requests
import os
import time
from PIL import Image, ImageDraw, ImageFont

POL_CF = 40007863    # Earth's circumference around poles
ECF = 40075016.686   # Earth's circumference around the equator



# icon_path = 'icons/120px-Firepit.png'
myfont = os.path.join(os.path.dirname(__file__), "DejaVuSansMono.ttf")
slope_tiles ="https://tiles.bergfex.at/data/europe-slope-11-15/{z}/{x}/{y}.png"

def getMap(index, coordinates, MAP_STYLE, ZOOM, tmpdir, slope=False):
    tiles_dir = os.path.join(str(tmpdir), "tiles")
    print(f"Using tiles directory: {tiles_dir}")
    nwLat, nwLon = coordinates['Northwest']
    seLat, seLon = coordinates['SouthEast']
    # nwLon, seLat, seLon, nwLat = coordinates

    WIDTH_METERS, HEIGHT_METERS = getMetersFromCoordinates(nwLat, seLat, seLon, nwLon)
    # Calculate tiles
    x1, y1 = deg2num(nwLat, nwLon, ZOOM)
    x2, y2 = deg2num(seLat, seLon, ZOOM)
    # Calculate Tile Corners Coordinates
    lat1, lon1 = num2deg(x1, y1, ZOOM)

    # Download Tiles
    print(f"Downloading Map {index+1} ...")
    download_tiles(x1, x2, y1, y2, ZOOM, MAP_STYLE, tiles_dir)
    output_image, tile_size = stitchTiles(x1, x2, y1, y2, ZOOM, tiles_dir)

    # Calculate Pixels per Meter
    latitude = math.radians((nwLat + seLat) / 2)
    s_pixel = ECF * math.cos(latitude) / (2.0 ** ZOOM * tile_size)
    pix_w = int(WIDTH_METERS / s_pixel)
    pix_h = int(HEIGHT_METERS / s_pixel)

    map_image = cropBorders(nwLat, nwLon, lon1, lat1, s_pixel, pix_w, pix_h, output_image)

    if slope:
        download_tiles(x1, x2, y1, y2, ZOOM, slope_tiles, tiles_dir, slope=True)
        output_image, tile_size = stitchTiles(x1, x2, y1, y2, ZOOM, tiles_dir, slope=True)
        s_pixel = ECF * math.cos(latitude) / (2.0 ** ZOOM * 512)
        pix_w = int(WIDTH_METERS / s_pixel)
        pix_h = int(HEIGHT_METERS / s_pixel)
        slope_image = cropBorders(nwLat, nwLon, lon1, lat1, s_pixel, pix_w, pix_h, output_image)
        # Apply 40% opacity to slope image
        map_rgba, slope_rgba = map_image.convert('RGBA'), slope_image.convert('RGBA')
        alpha = slope_rgba.split()[3]
        alpha = alpha.point(lambda p: int(p * 0.4))
        slope_rgba.putalpha(alpha)
        slope_resized = slope_rgba.resize(map_rgba.size, resample=Image.Resampling.LANCZOS)
        map_image = Image.alpha_composite(map_image.convert('RGBA'), slope_resized)

    map_image=label(map_image, s_pixel, tile_size, index)
    map_image = draw_firepits(map_image, coordinates, s_pixel)
    # map_image.show()
    map_image.save(os.path.join(str(tmpdir), f'Map{index + 1}.png'))





def getMetersFromCoordinates(north, south, east, west):
    widthMeters = (east - west) * (ECF * math.cos(math.radians((north+south)/2))) / 360
    heightMeters = (north - south) * POL_CF / 360
    return [widthMeters, heightMeters]


def getZoom(max_distance):
    return int(math.log((1.3*(POL_CF+ECF)/max_distance*2),2))


def heightFromCoordinates(north, south):
    return POL_CF*(north-south)/360


def widthFromCoordinates(west, east, latitude):
    return ECF*math.cos(math.radians(latitude))*(east-west)/360


def label(image, s_pixel, tile_size, index):
    pix1 = int(1000/s_pixel)
    line_width = int(tile_size/128)
    width, height = image.size
    ImageDraw.ImageDraw.font = ImageFont.truetype(myfont, int(tile_size/12))
    draw = ImageDraw.Draw(image)
    draw.text((width-10, height-10), f"Map {index+1}", fill=(255, 0, 0), anchor='rs', stroke_width=0)
    draw.line((10, height-10, 10+pix1, height-10), fill=(0, 0, 0), width=line_width)
    draw.line((10, height-15, 10, height-5), fill=(0, 0, 0), width=line_width)
    draw.line((10+pix1, height-15, 10+pix1, height-5), fill=(0, 0, 0), width=line_width)
    draw.text((10+(pix1/2), height-12), "1 km", fill=(0, 0, 0), anchor='ms', stroke_width=0)
    return image


def stitchTiles(x1, x2, y1, y2, ZOOM, tiles_dir, slope=False):
    # Initialize List for Tile Images
    tile_images = []

    # Stitch Tiles Together
    for y in range(y1, y2 + 1):
        row_images = []
        for x in range(x1, x2 + 1):
            if slope:
                tile_filename = os.path.join(tiles_dir, f"slope_tile_{ZOOM}_{x}_{y}.png")
            else:
                tile_filename = os.path.join(tiles_dir, f"map_tile_{ZOOM}_{x}_{y}.png")
            tile_image = Image.open(tile_filename)
            row_images.append(tile_image)
        tile_images.append(row_images)

    # Create a single image from tile_images
    image_width = sum(img.width for img in tile_images[0])
    image_height = sum(row[0].height for row in tile_images)
    output_image = Image.new("RGBA", (image_width, image_height))

    y_offset = 0
    for row_images in tile_images:
        x_offset = 0
        for tile_image in row_images:
            output_image.paste(tile_image, (x_offset, y_offset))
            x_offset += tile_image.width
        y_offset += row_images[0].height

    tile_size, _ = Image.open(os.path.join(tiles_dir, f'map_tile_{ZOOM}_{x1}_{y1}.png')).size
    # print(f"Tile size: {tile_size}")

    return output_image, tile_size


def cropBorders(northwest_latitude, northwest_longitude, lon1, lat1, s_pixel, pix_w, pix_h, output_image):

    left_crop = int((ECF * math.cos(math.radians(northwest_latitude)) * abs(lon1 - northwest_longitude) / 360) / s_pixel)
    top_crop = int((POL_CF * abs(lat1 - northwest_latitude) / 360) / s_pixel)
    right_crop = left_crop + pix_w
    bottom_crop = top_crop + pix_h

    cropped_image = output_image.crop((left_crop, top_crop, right_crop, bottom_crop))
    return cropped_image


def download_tiles(x1, x2, y1, y2, ZOOM, MAP_STYLE, tiles_dir, slope=False):
    # Create Directory for Tiles
    if not os.path.exists(tiles_dir):
        os.makedirs(tiles_dir)

    z = ZOOM
    # Loop Through Tiles and Download

    for x in range(x1, x2 + 1):
        for y in range(y1, y2 + 1):
            tile_url = MAP_STYLE.format(z=z, x=x, y=y)
            # print(tile_url)
            if slope:
                tile_filename = os.path.join(tiles_dir, f"slope_tile_{ZOOM}_{x}_{y}.png")
            else:
                tile_filename = os.path.join(tiles_dir, f"map_tile_{ZOOM}_{x}_{y}.png")
            if not os.path.exists(tile_filename):
                for attempt in range(3):  # Try up to 3 times
                    try:
                        response = requests.get(tile_url)
                        if response.status_code == 200:
                            with open(tile_filename, 'wb') as f:
                                f.write(response.content)
                            break  # Success, exit retry loop
                        else:
                            print(f"Failed to download {tile_url}: {response.status_code}")
                    except Exception as e:
                        print(f"Error downloading {tile_url}: {e}")
                    time.sleep(1)  # Wait 1 second before retrying
    print("Tiles Downloaded")


# Calculate Tile Coordinates
def deg2num(lat_deg, lon_deg, ZOOM):
    xtile = int((lon_deg + 180.0) / 360.0 * 2.0 ** ZOOM)
    lat_rad = math.radians(lat_deg)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) * 2.0 ** (ZOOM - 1.0))
    return xtile, ytile


# Calculate Tile Corners Coordinates
def num2deg(x, y, ZOOM):
    lon = (x / 2**ZOOM)*360-180
    lat = math.atan(math.sinh(math.pi-(y/2**ZOOM)*2*math.pi))*180/math.pi
    return lat, lon


def draw_firepits(image, coordinates, s_pixel):
    nwLat, nwLon = coordinates['Northwest']
    seLat, seLon = coordinates['SouthEast']
    # nwLon, seLat, seLon, nwLat = coordinates

    try:
        positions = []
        firepits = get_firepits(nwLat, nwLon, seLat, seLon)

        if not firepits:
            print("No firepits found or API failed, skipping firepit overlay")
            return image

        for firepit in firepits:
            # x_meters, y_meters = getMetersFromCoordinates(nwLat, firepit[0], firepit[1], nwLon)
            # x, y = int(x_meters / s_pixel), int(y_meters / s_pixel)
            x,y = get_xy(firepit[0], firepit[1], coordinates, image.width, image.height)
            positions.append((x, y))

        current_dir = os.path.dirname(os.path.realpath(__file__))
        parent_dir = os.path.dirname(current_dir)
        icon_path = os.path.join(parent_dir, 'icons/120px-Firepit.png')

        if not os.path.exists(icon_path):
            print(f"Firepit icon not found at {icon_path}, skipping firepit overlay")
            return image

        icon = Image.open(icon_path)
        icon = icon.resize((20, 20))
    except Exception as e:
        print(f"Error in draw_firepits: {e}")
        print("Continuing without firepit overlay")
        return image

    image = overlay_image(image, icon, positions)
    icon.close()
    return image


def overlay_image(image, icon, positions):
    for position in positions:
        image.paste(icon, position, icon)
    return image


def get_firepits(nwLat, nwLon, seLat, seLon):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
        node["leisure"="firepit"]({seLat},{nwLon},{nwLat},{seLon});
    );
    out center;
    """

    try:
        response = requests.get(overpass_url, params={'data': overpass_query}, timeout=10)
        print(f"Overpass API response status: {response.status_code}")

        if response.status_code != 200:
            print(f"Overpass API returned status {response.status_code}: {response.text}")
            return []

        if not response.text.strip():
            print("Overpass API returned empty response")
            return []

        data = response.json()
        print(f"Overpass API returned {len(data.get('elements', []))} firepit elements")

    except requests.exceptions.RequestException as e:
        print(f"Error making request to Overpass API: {e}")
        return []
    except ValueError as e:
        print(f"Error parsing JSON response from Overpass API: {e}")
        print(f"Response text: {response.text[:500]}")  # First 500 chars for debugging
        return []

    firepits = []
    for element in data.get('elements', []):
            if 'lat' in element and 'lon' in element:
                    firepits.append((element['lat'], element['lon']))
            elif 'center' in element:
                    firepits.append((element['center']['lat'], element['center']['lon']))

    return firepits

def get_xy(lat, lon, coordinates, pix_w, pix_h):
    nwLat, nwLon = coordinates['Northwest']
    seLat, seLon = coordinates['SouthEast']
    # nwLon, seLat, seLon, nwLat = coordinates

    x= int((lon - nwLon) / (seLon - nwLon) * pix_w)
    y= int((lat - nwLat) / (seLat - nwLat) * pix_h)

    return x, y
