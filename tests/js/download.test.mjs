/**
 * The download round-trip: the request body must stay byte-identical to what
 * the old script posted, and the response handling must still pick the right
 * filename.
 */

import assert from "node:assert/strict";
import test from "node:test";

import {
  DEFAULT_FILENAME,
  buildPayload,
  filenameFromDisposition,
  requestMap,
} from "../../static/js/download.js";
import { legacyPayload, seededRandom, stubBounds } from "./legacy.mjs";

const CONFIG = {
  width: 288,
  height: 201,
  scale: 25000,
  zoom: 14,
  autoZoom: true,
  upscale: false,
  overview: false,
  pdf: true,
  orientation: "landscape",
};

const RECTANGLE = {
  north: 49.29878484646142,
  south: 49.253568734818565,
  east: 7.975131646663512,
  west: 7.8759940704995755,
};

test("buildPayload maps bounds onto the Northwest/SouthEast contract", () => {
  const payload = buildPayload({
    rectangles: [RECTANGLE],
    markers: [],
    tileUrl: "https://tiles.example/{z}/{x}/{y}.png",
    slope: false,
    config: CONFIG,
  });

  assert.deepEqual(payload.coordinates_list, [
    { Northwest: [RECTANGLE.north, RECTANGLE.west], SouthEast: [RECTANGLE.south, RECTANGLE.east] },
  ]);
});

test("buildPayload serialises markers as plain lat/lng, as the backend reads them", () => {
  // Leaflet hands back `L.LatLng` instances, which may carry an `alt`.
  const latLng = { lat: 48.1, lng: 11.6, alt: 512 };

  const payload = buildPayload({
    rectangles: [],
    markers: [latLng],
    tileUrl: null,
    slope: false,
    config: CONFIG,
  });

  assert.deepEqual(payload.markerList, [{ lat: 48.1, lng: 11.6 }]);
});

test("buildPayload produces exactly the legacy request body", () => {
  const random = seededRandom(7);

  for (let i = 0; i < 200; i++) {
    const rectangles = Array.from({ length: 1 + Math.floor(random() * 3) }, () => {
      const south = random() * 80;
      const west = random() * 20;
      return { south, west, north: south + random(), east: west + random() };
    });
    const markers = Array.from({ length: Math.floor(random() * 3) }, () => ({
      lat: random() * 80,
      lng: random() * 20,
    }));
    const config = { ...CONFIG, scale: 1000 * Math.ceil(random() * 50), pdf: random() > 0.5 };
    const slope = random() > 0.5;
    const tileUrl = slope ? "https://a.example/{z}/{x}/{y}.png" : null;

    const actual = buildPayload({ rectangles, markers, tileUrl, slope, config });
    const expected = legacyPayload(rectangles.map(stubBounds), markers, tileUrl, config, slope);

    assert.equal(JSON.stringify(actual), JSON.stringify(expected));
  }
});

test("buildPayload sends every config key the backend reads", () => {
  const { config } = buildPayload({
    rectangles: [],
    markers: [],
    tileUrl: "u",
    slope: true,
    config: CONFIG,
  });

  // render_maps.py / get_map.py read exactly these.
  assert.deepEqual(Object.keys(config).sort(), [
    "autoZoom",
    "height",
    "overview",
    "pdf",
    "scale",
    "slope",
    "tileLayer",
    "upscale",
    "width",
    "zoom",
  ]);
});

test("filenameFromDisposition", () => {
  assert.equal(filenameFromDisposition('attachment; filename="MyMap.zip"'), "MyMap.zip");
  assert.equal(filenameFromDisposition('inline; filename="Map1.png"'), "Map1.png");
  assert.equal(filenameFromDisposition(null), DEFAULT_FILENAME);
  assert.equal(filenameFromDisposition("attachment"), DEFAULT_FILENAME);
  assert.equal(filenameFromDisposition(undefined, "other.pdf"), "other.pdf");
});

test("requestMap posts JSON and returns the blob with its filename", async () => {
  const calls = [];
  const fetchStub = async (url, init) => {
    calls.push({ url, init });
    return {
      ok: true,
      status: 200,
      headers: { get: () => 'attachment; filename="MyMap.pdf"' },
      blob: async () => "<pdf bytes>",
    };
  };

  const payload = { coordinates_list: [], config: {} };
  const result = await requestMap("/send_coordinates", payload, fetchStub);

  assert.deepEqual(result, { blob: "<pdf bytes>", filename: "MyMap.pdf" });
  assert.equal(calls[0].url, "/send_coordinates");
  assert.equal(calls[0].init.method, "POST");
  assert.equal(calls[0].init.headers["Content-Type"], "application/json");
  assert.deepEqual(JSON.parse(calls[0].init.body), payload);
});

test("requestMap raises on an error response", async () => {
  const fetchStub = async () => ({ ok: false, status: 500 });

  await assert.rejects(() => requestMap("/send_coordinates", {}, fetchStub), {
    message: "HTTP error! status: 500",
  });
});
