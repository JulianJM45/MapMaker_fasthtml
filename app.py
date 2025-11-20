import os
import shutil
import asyncio
from fasthtml.common import *
from starlette.responses import FileResponse
from collections import deque
from modules.ui import header, body
from modules.renderMaps import render_maps

app, rt = fast_app(exts='ws')

# Main page route
@rt('/')
def get():
    page = Html(
        Head(header()),
        Body(body(),
        )
    )
    return page

@rt('/send_coordinates', methods=['POST'])
async def send_coordinates(request):
    data = await request.json()
    print(data)
    file_path, file_name = render_maps(data)

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

    return CleanupFileResponse(path=file_path, filename=file_name, cleanup_dir="MyMaps")

serve()
