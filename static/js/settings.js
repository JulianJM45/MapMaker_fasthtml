/**
 * Configuration handling.
 *
 * Defaults come from Python (`modules/config.py`), serialised into the page as
 * a `<script type="application/json">` blob. Live values come straight off the
 * form controls, so the DOM -- not a mirrored JS object -- is the source of
 * truth for whatever the user has selected.
 */

export const SETTINGS_ID = "mapmaker-settings";

/** Field ids the configuration panel is built from. */
export const FIELDS = {
  scale: "scale",
  zoom: "zoom",
  autoZoom: "AutoZoom",
  png: "leftButton",
  portrait: "portraitButton",
};

/** Used when the page did not ship a settings blob (e.g. in isolation tests). */
export const FALLBACK_DEFAULTS = {
  width: 288,
  height: 201,
  scale: 25000,
  zoom: 14,
  autoZoom: true,
  pdf: true,
  orientation: "landscape",
};

/**
 * Read the settings blob rendered by `modules.ui.settings_json`.
 *
 * @param {Document} root
 * @returns {object} `{defaults, mapStart, tileLayers, slopeLayer, ...}`
 */
export function readSettings(root = document) {
  const el = root.getElementById(SETTINGS_ID);
  const settings = el ? JSON.parse(el.textContent) : {};
  return {
    tileLayers: [],
    slopeRanges: [],
    mapStart: { center: [0, 0], zoom: 1 },
    endpoints: { render: "/send_coordinates" },
    ...settings,
    defaults: { ...FALLBACK_DEFAULTS, ...settings.defaults },
  };
}

/**
 * The configuration as it currently stands in the form.
 *
 * Fields the panel does not expose fall back to `defaults`, and so does any
 * control that is missing from the DOM.
 *
 * @param {object} defaults
 * @param {Document} root
 */
export function readConfig(defaults, root = document) {
  const field = (id) => root.getElementById(id);
  const scale = field(FIELDS.scale);
  const zoom = field(FIELDS.zoom);
  const autoZoom = field(FIELDS.autoZoom);
  const png = field(FIELDS.png);
  const portrait = field(FIELDS.portrait);

  return {
    width: defaults.width,
    height: defaults.height,
    scale: scale ? Number.parseFloat(scale.value) : defaults.scale,
    zoom: zoom ? Number.parseInt(zoom.value) : defaults.zoom,
    autoZoom: autoZoom ? autoZoom.checked : defaults.autoZoom,
    upscale: defaults.upscale,
    overview: defaults.overview,
    pdf: png ? !png.checked : defaults.pdf,
    orientation: portrait
      ? portrait.checked
        ? "portrait"
        : "landscape"
      : defaults.orientation || "landscape",
  };
}
