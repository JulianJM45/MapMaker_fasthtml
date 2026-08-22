/**
 * A pinhole DOM.
 *
 * The frontend modules under test only ever call `getElementById` and read
 * `value` / `checked` / `textContent`, so a real DOM implementation would be
 * ceremony. Anything richer (Leaflet wiring, CSS-driven state) is covered by
 * the Python tests against the rendered page instead.
 */

/**
 * @param {Record<string, object>} elements  id -> element properties
 * @returns {{getElementById(id: string): object|null}}
 */
export function fakeDocument(elements) {
  return {
    getElementById: (id) => (id in elements ? elements[id] : null),
  };
}

/** The configuration panel as the browser sees it, with overridable state. */
export function fakePanel({
  scale = "25000",
  zoom = "14",
  autoZoom = true,
  png = false,
  portrait = false,
  settings = null,
} = {}) {
  const elements = {
    scale: { value: scale },
    zoom: { value: zoom },
    AutoZoom: { checked: autoZoom },
    leftButton: { checked: png },
    rightButton: { checked: !png },
    portraitButton: { checked: portrait },
    landscapeButton: { checked: !portrait },
  };
  if (settings) elements["mapmaker-settings"] = { textContent: JSON.stringify(settings) };
  return fakeDocument(elements);
}
