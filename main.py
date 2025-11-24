import os
import shutil
import asyncio
import random
# from asyncio import sleep

from fasthtml.common import *

from starlette.responses import FileResponse
from modules.ui import header, body
from modules.renderMaps import render_maps


hdrs=(Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js"),)
app,rt = fast_app(hdrs=hdrs, pico=False)

message_queue = asyncio.Queue()
shutdown_event = signal_shutdown()



@rt('/')
def get():
    page= Head(header()), Body(body()),
    # sse = Div(hx_ext='sse', sse_connect='/send-message', hx_swap="beforeend show:bottom", sse_swap="message",id='log')
    sse = Div(hx_ext='sse', sse_connect='/send-message', hx_swap="beforeend", sse_swap="message",id='log')
    return page, sse


async def message_generator():
    while not shutdown_event.is_set():
        try:
            # Wait for a message from the queue with timeout
            message = await asyncio.wait_for(message_queue.get(), timeout=1.0)
            yield sse_message(Div(message))
        except asyncio.TimeoutError:
            # Send keepalive to prevent connection timeout
            continue
        except Exception as e:
            print(f"SSE error: {e}")
            break

@rt("/send-message")
async def get():
    return EventStream(message_generator())

async def send_msg(msg: str):
    await message_queue.put(msg)


@rt('/send_coordinates', methods=['POST'])
async def send_coordinates(request):
    data = await request.json()

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
        file_path, file_name, tmpdir = await render_maps(data, send_msg)
        return CleanupFileResponse(path=file_path, filename=file_name, cleanup_dir=tmpdir)
    else:
        await send_msg("No coordinates provided")
        return {"message": "No coordinates provided"}



serve()
