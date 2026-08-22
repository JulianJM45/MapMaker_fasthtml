/**
 * Configuration reading: defaults come from the page, live values from the
 * form controls, and the result must match what the old `getConfigFromForm`
 * produced for the same inputs.
 */

import assert from "node:assert/strict";
import test from "node:test";

import { FALLBACK_DEFAULTS, FIELDS, readConfig, readSettings } from "../../static/js/settings.js";
import { fakeDocument, fakePanel } from "./dom.mjs";
import { getConfigFromForm } from "./legacy.mjs";

const PYTHON_DEFAULTS = {
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

test("readSettings parses the injected blob", () => {
  const settings = { defaults: { scale: 50000 }, mapStart: { center: [1, 2], zoom: 9 } };
  const doc = fakeDocument({ "mapmaker-settings": { textContent: JSON.stringify(settings) } });

  const result = readSettings(doc);

  assert.equal(result.mapStart.zoom, 9);
  assert.equal(result.defaults.scale, 50000, "page values win");
  assert.equal(result.defaults.width, FALLBACK_DEFAULTS.width, "missing keys fall back");
});

test("readSettings survives a page with no blob at all", () => {
  const result = readSettings(fakeDocument({}));

  assert.deepEqual(result.defaults, FALLBACK_DEFAULTS);
  assert.deepEqual(result.tileLayers, []);
  assert.equal(result.endpoints.render, "/send_coordinates");
});

test("readConfig reflects the panel defaults", () => {
  assert.deepEqual(readConfig(PYTHON_DEFAULTS, fakePanel()), PYTHON_DEFAULTS);
});

test("readConfig reads scale, zoom and AutoZoom off the form", () => {
  const config = readConfig(
    PYTHON_DEFAULTS,
    fakePanel({ scale: "10000", zoom: "17", autoZoom: false }),
  );

  assert.equal(config.scale, 10000);
  assert.equal(config.zoom, 17);
  assert.equal(config.autoZoom, false);
});

test("readConfig reads the format and orientation pills", () => {
  assert.equal(readConfig(PYTHON_DEFAULTS, fakePanel({ png: true })).pdf, false);
  assert.equal(readConfig(PYTHON_DEFAULTS, fakePanel({ png: false })).pdf, true);
  assert.equal(readConfig(PYTHON_DEFAULTS, fakePanel({ portrait: true })).orientation, "portrait");
  assert.equal(readConfig(PYTHON_DEFAULTS, fakePanel({ portrait: false })).orientation, "landscape");
});

test("readConfig falls back to the defaults when controls are absent", () => {
  assert.deepEqual(readConfig(PYTHON_DEFAULTS, fakeDocument({})), PYTHON_DEFAULTS);
});

test("readConfig agrees with the legacy getConfigFromForm on the shared fields", () => {
  for (const scale of ["25000", "10000", "1"]) {
    for (const zoom of ["14", "9", "18"]) {
      for (const autoZoom of [true, false]) {
        const doc = fakePanel({ scale, zoom, autoZoom });
        const actual = readConfig(PYTHON_DEFAULTS, doc);
        const legacy = getConfigFromForm(
          {
            scaleInput: { value: scale },
            zoomInput: { value: zoom },
            autoZoomCheckbox: { checked: autoZoom },
          },
          undefined, // window.DEFAULT_CONFIG was never actually set
        );

        // prettier-ignore
        const shared = [
          "width", "height", "scale", "zoom", "autoZoom", "pdf", "orientation",
        ];
        for (const key of shared) {
          assert.equal(actual[key], legacy[key], `${key} @ scale=${scale} zoom=${zoom}`);
        }
      }
    }
  }
});

test("the legacy fallback config the browser really used matches Python's defaults", () => {
  // The old script referenced `window.DEFAULT_CONFIG`, which nothing ever set,
  // so this literal is what shipped. It must agree with modules/config.py.
  const legacy = getConfigFromForm({}, undefined);

  assert.equal(legacy.width, PYTHON_DEFAULTS.width);
  assert.equal(legacy.height, PYTHON_DEFAULTS.height);
  assert.equal(legacy.scale, PYTHON_DEFAULTS.scale);
  assert.equal(legacy.zoom, PYTHON_DEFAULTS.zoom);
  assert.equal(legacy.autoZoom, PYTHON_DEFAULTS.autoZoom);
  assert.equal(legacy.pdf, PYTHON_DEFAULTS.pdf);
  assert.equal(legacy.orientation, PYTHON_DEFAULTS.orientation);
});

test("FIELDS names the ids the page renders", () => {
  assert.deepEqual(Object.values(FIELDS).sort(), [
    "AutoZoom",
    "leftButton",
    "portraitButton",
    "scale",
    "zoom",
  ]);
});
