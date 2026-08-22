"""Fixtures for the browser tests.

Skipped unless Playwright is installed:

    uv sync --group e2e && uv run playwright install chromium
    uv run pytest -m e2e
"""

import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

import pytest

playwright_api = pytest.importorskip(
    "playwright.sync_api", reason="playwright is not installed"
)

ROOT = Path(__file__).resolve().parent.parent.parent

# Patched in before Leaflet's own script assigns `window.L`, so the test can
# reach the map instance the app creates without the app exporting it.
EXPOSE_MAP = """
let namespace;
Object.defineProperty(window, "L", {
  configurable: true,
  get: () => namespace,
  set(value) {
    namespace = value;
    if (value && typeof value.map === "function" && !value.map.__exposed) {
      const create = value.map;
      const wrapped = function (...args) {
        const map = create.apply(this, args);
        window.__map = map;
        return map;
      };
      Object.assign(wrapped, create);
      wrapped.__exposed = true;
      value.map = wrapped;
    }
  },
});
"""


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def server():
    """A real uvicorn process, so the browser sees the app as deployed."""
    port = _free_port()
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    url = f"http://127.0.0.1:{port}"
    try:
        for _ in range(100):
            try:
                urlopen(url, timeout=1)
                break
            except URLError:
                time.sleep(0.2)
        else:
            raise RuntimeError("the app did not start")
        yield url
    finally:
        process.terminate()
        process.wait(timeout=10)


@pytest.fixture(scope="session")
def browser():
    with playwright_api.sync_playwright() as playwright:
        instance = playwright.chromium.launch()
        yield instance
        instance.close()


@pytest.fixture
def app_page(browser, server):
    """A loaded page, with console errors collected and asserted empty."""
    context = browser.new_context(viewport={"width": 1280, "height": 900})
    context.add_init_script(EXPOSE_MAP)
    page = context.new_page()
    page.console_errors = []
    page.on(
        "console", lambda m: m.type == "error" and page.console_errors.append(m.text)
    )
    page.on("pageerror", lambda e: page.console_errors.append(str(e)))

    page.goto(server, wait_until="networkidle")
    page.wait_for_function("window.__map !== undefined")

    yield page

    assert page.console_errors == []
    context.close()
