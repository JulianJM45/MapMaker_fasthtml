import os
import shutil
import asyncio

from fasthtml.common import *
from collections import deque

from starlette.responses import FileResponse
from modules.ui import header, body
from modules.renderMaps import render_maps

# app, rt = fast_app(exts='ws')
app, rt = fast_app(exts='ws', pico=False)

# All messages here, but only most recent 15 are stored
messages = deque(maxlen=5)
users = {}

# Takes all the messages and renders them
# box_style = "border: 1px solid #ccc; border-radius: 10px; padding: 10px; margin: 5px 0;"
def render_messages(messages):
    return Div(*[Div(m, style="font-size: 18px;") for m in messages], id='log')


@rt('/')
def get():
    page= Head(header()), Body(body()),
    websocket = Div(
        Div(render_messages(messages),id='log'), # All the Messages
        hx_ext='ws', ws_connect='ws') # Use a web socket
    return page, websocket

def on_connect(ws, send): users[id(ws)] = send
def on_disconnect(ws):users.pop(id(ws),None)

@app.ws('/ws', conn=on_connect, disconn=on_disconnect)
async def ws(msg:str):
    messages.appendleft(msg) # New messages first
    for u in users.values(): # Get `send` function for a user
        await u(render_messages(messages)) # Send the message to that user

@rt('/send_coordinates', methods=['POST'])
async def send_coordinates(request):
    data = await request.json()
    # await ws("ws connected")
    # await asyncio.sleep(0.1)

    # Custom FileResponse that cleans up after sending
    class CleanupFileResponse(FileResponse):
        def __init__(self, *args, cleanup_dir=None, **kwargs):
            super().__init__(*args, **kwargs)
            self.cleanup_dir = cleanup_dir

        async def __call__(self, scope, receive, send):
            try:
                # Send the file
                await super().__call__(scope, receive, send)
            finally:
                # Clean up after file has been sent
                if self.cleanup_dir and os.path.exists(self.cleanup_dir):
                    # Add small delay to ensure file transfer is complete
                    await asyncio.sleep(0.1)
                    try:
                        shutil.rmtree(self.cleanup_dir)
                    except Exception as e:
                        print(f"Cleanup error: {e}")

    if data.get("coordinates_list", []):
        file_path, file_name, tmpdir = await render_maps(data, ws)
        return CleanupFileResponse(path=file_path, filename=file_name, cleanup_dir=tmpdir)
    else: await ws("No coordinates provided")



serve()
