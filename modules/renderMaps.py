import os
import subprocess
import zipfile
import io
import shutil
import re
import img2pdf
import asyncio

from .get_map import *
# from utils import send_message


async def render_maps(data, ws_send=None):
    if ws_send:
        await ws_send("Receiving coordinates...")
        await asyncio.sleep(0.01)  # Allow message to be sent
    # print(str(data))
    # Extract coordinates_list and config
    coordinates_list = data.get("coordinates_list", [])
    config = data.get("config", {})

    # Log the extracted data
    # send_message('Coordinates received: ' + str(coordinates_list))
    # send_message('Config received: ' + str(config))

    # Access individual config values
    MAP_STYLE = config.get("tileLayer")
    WIDTH = int(config.get("width"))
    HEIGHT = int(config.get("height"))
    SCALE = int(config.get("scale"))
    ZOOM = int(config.get("zoom"))
    AutoZoom = config.get("autoZoom")
    upscale = config.get("upscale")
    Overview = config.get("overview")
    PDF = config.get("pdf")

    # print("Sending coordinates to Python:", coordinates_list)
    # print("Selected Tile Layer:", MAP_STYLE)
    # if upscale: print("upscaling")
    # else: print ("no upscaling")
    # max_distance=max(WIDTH, HEIGHT)
    # if AutoZoom: ZOOM = getZoom(max_distance *SCALE/1000)
    # print (ZOOM)

    if not os.path.exists("MyMaps"):
        os.makedirs("MyMaps")
    odd_maps = []
    even_maps = []

    if len(coordinates_list) > 1:
        Overview = True

    if Overview:
        if ws_send:
            await ws_send("Loading Overview Map...")
            await asyncio.sleep(0.01)  # Allow message to be sent
        overviewImage, ovmc = overviewMap(coordinates_list, MAP_STYLE, WIDTH, HEIGHT)

    for index, coordinates in enumerate(coordinates_list):
        if ws_send:
            await ws_send(f"Loading Map {index + 1}/{len(coordinates_list)}...")
            await asyncio.sleep(0.01)  # Allow message to be sent
        getMap(index, coordinates, MAP_STYLE, ZOOM)
        # Extract and assign the coordinates to separate variables

        if index % 2 == 0:
            odd_maps.append(f"./MyMaps/Map{index + 1}.png")
        else:
            even_maps.append(f"./MyMaps/Map{index + 1}.png")
        if Overview:
            overviewImage = drawMapInOverview(overviewImage, ovmc, coordinates, index)

    # Delete the "tiles" directory and its contents
    if os.path.exists("tiles"):
        shutil.rmtree("tiles")
        pass

    # Upscale the images if applicable
    # if upscale:
    #     send_message_to_js("Upscaling maps...")
    #     map_files = os.listdir('MyMaps')
    #     for map_file in map_files:
    #         if 'OverviewMap' in map_file: continue  # Skip this iteration
    #         upscaling(map_file, send_message_to_js)
    #     print('upscale finished :)')
    #     send_message_to_js("Upscale finished")

    image_paths = odd_maps + even_maps
    if Overview:
        overviewImage.save("MyMaps/OverviewMap.png")
        image_paths.append("MyMaps/OverviewMap.png")

    if PDF:
        if ws_send:
            await ws_send("Generating PDF...")
            await asyncio.sleep(0.01)
        print("Image paths:", image_paths)
        file_path = PDFgen(image_paths)
        print("pdf finished :)")

    elif len(image_paths) > 1:
        if ws_send:
            await ws_send("Creating ZIP archive...")
            await asyncio.sleep(0.01)
        file_path = Zipgen(image_paths)
        print("zip finished :)")

    else:
        file_path = "./MyMaps/Map1.png"
        # Maps = PNGgen(image_paths)
        # print('png finished :)')

    file_name = file_path.split("/")[-1]

    # if os.path.exists("MyMaps"):
    #     shutil.rmtree("MyMaps")

    if ws_send:
        await ws_send("Maps ready! Starting download...")
        await asyncio.sleep(0.01)  # Allow final message to be sent

    return file_path, file_name


def drawMapInOverview(overviewImage, ovmc, coordinates, index):
    width, height = overviewImage.size
    transparent_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(transparent_layer)
    fill_color = (0, 100, 255, 30)  # Blue with 50% transparency (RGBA)
    outline_color = (24, 116, 205, 200)  # Blue without transparency (RGB)
    nwLat, nwLon = coordinates['Northwest']
    seLat, seLon = coordinates['SouthEast']
    # nwLon, seLat, seLon, nwLat = coordinates
    x1 = width * (abs(nwLon - ovmc[1]) / abs(ovmc[1] - ovmc[3]))
    y1 = height * (abs(nwLat - ovmc[0]) / abs(ovmc[0] - ovmc[2]))
    x2 = width * (abs(seLon - ovmc[1]) / abs(ovmc[1] - ovmc[3]))
    y2 = height * (abs(seLat - ovmc[0]) / abs(ovmc[0] - ovmc[2]))
    draw.rectangle([x1, y1, x2, y2], fill=fill_color)
    draw.rectangle([x1, y1, x2, y2], outline=outline_color, width=4)
    # Add a number in the middle of the rectangle
    number = str(index + 1)
    font = ImageFont.truetype(myfont, size=50)  # Adjust the path and size
    text_x = (x1 + x2) // 2
    text_y = (y1 + y2) // 2
    draw.text(
        (text_x, text_y),
        number,
        fill=(0, 0, 255),
        anchor="mm",
        font=font,
        stroke_width=1,
    )
    overviewImage.paste(transparent_layer, (0, 0), transparent_layer)
    return overviewImage


def overviewMap(coordinates_list, MAP_STYLE, WIDTH, HEIGHT):
    # Initialize variables to store the maximum values
    max_north = max_south = max_east = max_west = None

    for coordinates in coordinates_list:
        nwLat, nwLon = coordinates['Northwest']
        seLat, seLon = coordinates['SouthEast']
        # nwLon, seLat, seLon, nwLat = coordinates

        if max_north is None or nwLat > max_north:
            max_north = nwLat
        if max_south is None or seLat < max_south:
            max_south = seLat
        if max_east is None or seLon > max_east:
            max_east = seLon
        if max_west is None or nwLon < max_west:
            max_west = nwLon

    # At this point, all max_ variables should be set to float values
    # Add type assertions to help the type checker
    assert max_north is not None
    assert max_south is not None
    assert max_east is not None
    assert max_west is not None

    max_north = max_north + 0.01
    max_west = max_west - 0.01
    max_south = max_south - 0.01
    max_east = max_east + 0.01

    latitude = (max_north + max_south) / 2
    longitude = (max_east + max_west) / 2
    HEIGHT_METERS = heightFromCoordinates(max_north, max_south)
    WIDTH_METERS = widthFromCoordinates(max_west, max_east, latitude)
    max_distance = max(HEIGHT_METERS, WIDTH_METERS)
    ZOOM = getZoom(max_distance)
    # rescaling
    if WIDTH_METERS > (HEIGHT_METERS * WIDTH / HEIGHT):
        HEIGHT_METERS = WIDTH_METERS * HEIGHT / WIDTH
        max_north = latitude + 360 * (HEIGHT_METERS / 2) / POL_CF
        max_south = latitude - 360 * (HEIGHT_METERS / 2) / POL_CF
    elif HEIGHT_METERS > (WIDTH_METERS * HEIGHT / WIDTH):
        WIDTH_METERS = HEIGHT_METERS * WIDTH / HEIGHT
        max_east = longitude + 360 * (WIDTH_METERS / 2) / (
            ECF * math.cos(math.radians(latitude))
        )
        max_west = longitude - 360 * (WIDTH_METERS / 2) / (
            ECF * math.cos(math.radians(latitude))
        )
    # Calculate Pixel Dimensions
    # s_pixel = ECF * math.cos(math.radians(latitude)) / 2.0 ** (ZOOM + 8.0)
    # pix_w = int(width / s_pixel)
    # pix_h = int(height / s_pixel)
    # Calculate tiles
    x1, y1 = deg2num(max_north, max_west, ZOOM)
    x2, y2 = deg2num(max_south, max_east, ZOOM)
    # Calculate Tile Corners Coordinates
    lat1, lon1 = num2deg(x1, y1, ZOOM)
    ovmc = [
        max_north,
        max_west,
        max_south,
        max_east,
    ]  # ovmc stands for overview map coordinates
    print("Downloading Overview Map ...")
    download_tiles(x1, x2, y1, y2, ZOOM, MAP_STYLE)
    # create output Image
    overviewImage, tile_size = stitchTiles(x1, x2, y1, y2, ZOOM)

    # Calculate Pixels per Meter
    s_pixel = ECF * math.cos(math.radians(latitude)) / (2.0**ZOOM * tile_size)
    # Calculate Pixel Dimensions
    pix_w = int(WIDTH_METERS / s_pixel)
    pix_h = int(HEIGHT_METERS / s_pixel)

    overviewImage = cropBorders(
        max_north, max_west, lon1, lat1, s_pixel, pix_w, pix_h, overviewImage
    )
    return overviewImage, ovmc


def PDFgen(image_paths):
    # Read each image in binary mode
    image_bytes_list = []
    for path in image_paths:
        with open(path, "rb") as f:
            image_bytes_list.append(f.read())

    # Now convert the list of bytes objects to a PDF
    pdf_buffer = io.BytesIO()
    pdf_buffer.write(img2pdf.convert(image_bytes_list))

    # Ensure the buffer is positioned at the beginning
    pdf_buffer.seek(0)

    file_path = "./MyMaps/MyMap.pdf"

    # Save the PDF to the MyMaps directory
    with open(file_path, "wb") as f:
        f.write(pdf_buffer.getvalue())

    return file_path


# def PNGgen(image_paths):
#     # Open the first image
#     image = Image.open(image_paths[0])
#     # Create a new image with the same size and mode
#     png_buffer = io.BytesIO()
#     image.save(png_buffer, format='PNG')
#     png_buffer.seek(0)
#     return png_buffer


def Zipgen(image_paths):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for path in image_paths:
            zip_file.write(path, os.path.basename(path))
    zip_buffer.seek(0)

    file_path = "./MyMaps/MyMap.zip"
    with open(file_path, "wb") as f:
        f.write(zip_buffer.getvalue())
    return file_path


def upscaling(map_file, print_message):
    map_file_without_extension, _ = os.path.splitext(map_file)

    current_dir = os.path.dirname(os.path.realpath(__file__))

    # Define the command as a list of strings
    executable = "realesrgan-ncnn-vulkan"
    executablefile = os.path.join(current_dir, executable)

    command = [
        executablefile,
        "-i",
        f"MyMaps/{map_file}",
        "-o",
        f"MyMaps/{map_file}",
        "-n",
        "realesrgan-x4plus",
    ]
    # Run the command
    process = subprocess.Popen(command, stderr=subprocess.PIPE, text=True)
    if process.stderr is not None:
        for line in iter(process.stderr.readline, ""):
            print(line, end="")
            # Extract the number
            match = re.search(r"(\d+.\d+)%", line)
            if match:
                number = float(match.group(1).replace(",", "."))
                # print('Progress:', number)
                print_message(f"upscaling {map_file_without_extension}:\u2003{number}%")
