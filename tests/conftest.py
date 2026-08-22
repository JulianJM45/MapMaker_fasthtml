"""Shared fixtures: a tiny HTML index, and an offline map-rendering harness."""

import asyncio
import io
import sys
from html.parser import HTMLParser
from pathlib import Path

import pytest
from PIL import Image
from starlette.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import main
from modules import get_map
from modules.render_maps import render_maps

TILE_SIZE = 256


class Element:
    """One parsed tag: its name, attributes and immediate text."""

    def __init__(self, tag, attrs):
        self.tag = tag
        self.attrs = dict(attrs)
        self.text = ""

    def __getitem__(self, name):
        return self.attrs[name]

    def get(self, name, default=None):
        return self.attrs.get(name, default)

    def __repr__(self):
        return f"<{self.tag} {self.attrs}>"


class Page(HTMLParser):
    """Index a rendered page by id and by tag.

    Only what the tests need: `page["log"]`, `page.by_tag("link")`, and the
    document order of ids so sibling-based CSS selectors can be verified.
    """

    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.by_id = {}
        self.tags = []
        self.id_order = []
        self._open = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        element = Element(tag, attrs)
        self.tags.append(element)
        if "id" in element.attrs:
            self.by_id[element["id"]] = element
            self.id_order.append(element["id"])
        if tag not in ("br", "input", "link", "meta", "img"):
            self._open.append(element)

    def handle_endtag(self, tag):
        if self._open and self._open[-1].tag == tag:
            self._open.pop()

    def handle_data(self, data):
        if self._open:
            self._open[-1].text += data

    def __contains__(self, element_id):
        return element_id in self.by_id

    def __getitem__(self, element_id):
        assert element_id in self.by_id, (
            f"#{element_id} missing; have {sorted(self.by_id)}"
        )
        return self.by_id[element_id]

    def by_tag(self, tag):
        return [e for e in self.tags if e.tag == tag]


@pytest.fixture(scope="session")
def client():
    return TestClient(main.app)


@pytest.fixture(scope="session")
def page(client):
    response = client.get("/")
    assert response.status_code == 200
    return Page(response.text)


@pytest.fixture(scope="session")
def styles():
    return (ROOT / "static" / "styles.css").read_text()


# --- offline rendering --------------------------------------------------------


class FakeTileResponse:
    """A solid-colour PNG, standing in for any tile server."""

    status_code = 200

    def __init__(self, url):
        self.url = url
        buffer = io.BytesIO()
        Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (200, 220, 255, 255)).save(
            buffer, format="PNG"
        )
        self.content = buffer.getvalue()


@pytest.fixture
def tile_server(monkeypatch):
    """Serve every tile locally and stub Overpass; returns the requested URLs."""
    requested = []

    def fake_get(url, **kwargs):
        requested.append(url)
        return FakeTileResponse(url)

    monkeypatch.setattr(get_map.requests, "get", fake_get)
    monkeypatch.setattr(get_map, "get_icons", lambda coordinates, symbol="firepit": [])
    return requested


@pytest.fixture(autouse=True)
def reset_marker_state():
    """`get_map` accumulates markers in a module global; isolate the tests."""
    get_map.markerList.clear()
    yield
    get_map.markerList.clear()


class Rendered:
    """What one `render_maps` run produced."""

    def __init__(self, file_path, file_name, tmpdir, messages):
        self.path = Path(file_path)
        self.name = file_name
        self.tmpdir = Path(tmpdir)
        self.messages = messages


@pytest.fixture
def render(tile_server):
    """Run the full render pipeline against the stubbed tile server."""

    def run(data):
        messages = []

        async def collect(message):
            messages.append(message)

        file_path, file_name, tmpdir = asyncio.run(render_maps(data, collect))
        return Rendered(file_path, file_name, tmpdir, messages)

    return run


@pytest.fixture
def render_live():
    """Same as `render`, but against the real tile servers (`-m network`)."""

    def run(data):
        messages = []

        async def collect(message):
            messages.append(message)

        file_path, file_name, tmpdir = asyncio.run(render_maps(data, collect))
        return Rendered(file_path, file_name, tmpdir, messages)

    return run
