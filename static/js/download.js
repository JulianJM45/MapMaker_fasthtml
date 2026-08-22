/**
 * Turning the current selection into a downloaded map.
 *
 * `buildPayload` and `filenameFromDisposition` are pure so the wire format can
 * be pinned by tests; `requestMap` and `saveBlob` are the thin browser layer.
 */

/** Falls back to this when the server sends no `Content-Disposition`. */
export const DEFAULT_FILENAME = "MyMap.pdf";

/**
 * The JSON body `POST /send_coordinates` expects.
 *
 * @param {object}   selection
 * @param {Array<{north:number,south:number,east:number,west:number}>} selection.rectangles
 * @param {Array<{lat:number,lng:number}>} selection.markers
 * @param {string|null} selection.tileUrl  template of the active base layer
 * @param {boolean}  selection.slope       is the slope overlay switched on
 * @param {object}   selection.config      see `settings.readConfig`
 */
export function buildPayload({ rectangles, markers, tileUrl, slope, config }) {
  return {
    coordinates_list: rectangles.map(({ north, south, east, west }) => ({
      Northwest: [north, west],
      SouthEast: [south, east],
    })),
    markerList: markers.map(({ lat, lng }) => ({ lat, lng })),
    config: {
      tileLayer: tileUrl,
      width: config.width,
      height: config.height,
      scale: config.scale,
      zoom: config.zoom,
      autoZoom: config.autoZoom,
      upscale: config.upscale,
      overview: config.overview,
      pdf: config.pdf,
      slope,
    },
  };
}

/** Pull `filename="..."` out of a `Content-Disposition` header. */
export function filenameFromDisposition(header, fallback = DEFAULT_FILENAME) {
  const match = header?.match(/filename="([^"]+)"/);
  return match ? match[1] : fallback;
}

/**
 * POST the payload and hand back the rendered file.
 *
 * @returns {Promise<{blob: Blob, filename: string}>}
 * @throws {Error} on a non-2xx response
 */
export async function requestMap(url, payload, fetchImpl = fetch) {
  const response = await fetchImpl(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

  return {
    blob: await response.blob(),
    filename: filenameFromDisposition(response.headers.get("Content-Disposition")),
  };
}

/** Trigger a browser download for an in-memory blob. */
export function saveBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = Object.assign(document.createElement("a"), {
    href: url,
    download: filename,
  });
  link.style.display = "none";
  document.body.append(link);
  link.click();
  URL.revokeObjectURL(url);
  link.remove();
}
