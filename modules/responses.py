"""Custom Starlette responses."""

import asyncio
import shutil

from starlette.responses import FileResponse


class CleanupFileResponse(FileResponse):
    """Serve a file, then delete the temporary directory it came from."""

    def __init__(self, *args, cleanup_dir=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cleanup_dir = cleanup_dir

    async def __call__(self, scope, receive, send):
        try:
            await super().__call__(scope, receive, send)
        finally:
            await self._cleanup()

    async def _cleanup(self):
        if not self.cleanup_dir:
            return
        # Give the transfer a moment to drain before pulling the rug out.
        await asyncio.sleep(0.1)
        try:
            shutil.rmtree(self.cleanup_dir)
        except FileNotFoundError:
            pass
        except OSError as e:
            print(f"Cleanup error: {e}")
