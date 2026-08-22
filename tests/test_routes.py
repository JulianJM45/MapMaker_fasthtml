"""HTTP surface: the routes and static assets the frontend depends on."""

import asyncio
import json

import main
from modules import config as cfg


def test_index_renders(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")


def test_biwaks_endpoint_returns_coordinate_pairs(client):
    response = client.get("/api/biwaks")

    assert response.status_code == 200
    points = response.json()
    assert isinstance(points, list) and points
    for lat, lon in points:
        assert -90 <= lat <= 90
        assert -180 <= lon <= 180


def test_biwaks_endpoint_does_not_depend_on_the_working_directory(
    client, monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)

    assert client.get("/api/biwaks").status_code == 200


def test_send_coordinates_rejects_an_empty_selection(client):
    response = client.post(
        "/send_coordinates", json={"coordinates_list": [], "config": {}}
    )

    assert response.status_code == 200
    assert response.json() == {"message": "No coordinates provided"}


def test_send_coordinates_rejects_a_body_with_no_selection_key(client):
    assert client.post("/send_coordinates", json={}).json() == {
        "message": "No coordinates provided"
    }


def test_static_assets_are_served(client):
    for path in [cfg.LOCAL_CSS, cfg.LOCAL_JS, cfg.FAVICON, cfg.KOTHE_ICON]:
        assert client.get(path).status_code == 200, path


def test_every_frontend_module_is_served(client):
    for module in ["app.js", "geo.js", "layers.js", "settings.js", "download.js"]:
        assert client.get(f"/static/js/{module}").status_code == 200, module


def test_progress_messages_reach_the_sse_generator():
    """`send_msg` -> queue -> `message_generator`, the path the log renders."""

    async def first_message():
        while not main.message_queue.empty():  # messages other tests queued up
            main.message_queue.get_nowait()

        stream = main.message_generator()
        await main.send_msg("Loading Map 1/1...")
        try:
            return await asyncio.wait_for(anext(stream), timeout=5)
        finally:
            await stream.aclose()

    chunk = asyncio.run(first_message())

    assert "Loading Map 1/1..." in chunk
    assert chunk.startswith("event: message")


def test_browser_settings_are_json_serialisable():
    settings = cfg.browser_settings()

    assert json.loads(json.dumps(settings)) == settings
