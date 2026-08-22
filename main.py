"""MapMaker -- draw regions on a map, get a printable PDF or PNG bundle back."""

import asyncio
import json
from pathlib import Path

from fasthtml.common import *

from modules import ui
from modules.render_maps import render_maps
from modules.responses import CleanupFileResponse

BIWAKS_FILE = Path(__file__).parent / "data" / "KPE_Biwak.json"

app, rt = fast_app(hdrs=ui.headers(), pico=False)

message_queue = asyncio.Queue()
shutdown_event = signal_shutdown()


@rt("/")
def get():
    return ui.page()


@app.get("/api/biwaks")
def biwaks():
    return JSONResponse(json.loads(BIWAKS_FILE.read_text()))


@rt("/send-message")
async def get_see():
    return EventStream(message_generator())


async def message_generator():
    """Drain the progress queue into the page's SSE log until shutdown."""
    while not shutdown_event.is_set():
        try:
            message = await asyncio.wait_for(message_queue.get(), timeout=1.0)
            yield sse_message(Div(message))
        except TimeoutError:
            continue
        except Exception as e:
            print(f"SSE error: {e}")
            break


async def send_msg(msg: str):
    await message_queue.put(msg)


@rt("/send_coordinates", methods=["POST"])
async def send_coordinates(request):
    data = await request.json()
    if not data.get("coordinates_list", []):
        await send_msg("No coordinates provided")
        return {"message": "No coordinates provided"}

    file_path, file_name, tmpdir = await render_maps(data, send_msg)
    return CleanupFileResponse(path=file_path, filename=file_name, cleanup_dir=tmpdir)


serve()
