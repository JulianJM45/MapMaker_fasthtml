/**
 * Drives the real frontend modules headlessly and prints the request body they
 * would POST. Used by `tests/test_contract.py` to feed the actual browser
 * payload into the Python renderer.
 *
 * Usage: node tests/build_payload.mjs <settings.json>
 */

import { readFileSync } from "node:fs";

import { buildPayload } from "../static/js/download.js";
import { boundsFromMeters, pageMeters } from "../static/js/geo.js";
import { readConfig, readSettings } from "../static/js/settings.js";

const settingsJson = readFileSync(process.argv[2], "utf8");

// The panel exactly as `modules/ui.py` renders it, plus the settings blob.
const document = {
  getElementById: (id) =>
    ({
      "mapmaker-settings": { textContent: settingsJson },
      scale: { value: "25000" },
      zoom: { value: "13" },
      AutoZoom: { checked: false },
      leftButton: { checked: false }, // bundled PDF
      portraitButton: { checked: false }, // landscape
    })[id] ?? null,
};

const settings = readSettings(document);
const config = readConfig(settings.defaults, document);

// One rectangle drawn near Munich, snapped to a page like `draw:created` does.
const { widthMeters, heightMeters } = pageMeters(config);
const rectangle = boundsFromMeters({ lat: 49.276, lng: 7.925 }, widthMeters, heightMeters);

process.stdout.write(
  JSON.stringify(
    buildPayload({
      rectangles: [rectangle],
      markers: [{ lat: 49.276, lng: 7.925 }],
      tileUrl: settings.tileLayers[0].url,
      slope: false,
      config,
    }),
  ),
);
