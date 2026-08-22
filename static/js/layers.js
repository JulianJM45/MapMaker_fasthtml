/**
 * Leaflet layer set-up: base maps, the slope overlay and its legend, and the
 * bivouac markers. Everything is driven by the settings blob from Python.
 */

/**
 * Build the tile layers, register the layer control and remember which base
 * layer is active.
 *
 * @param {L.Map} map
 * @param {{tileLayers: Array, slopeLayer: object}} settings
 * @returns {{slopeLayer: L.TileLayer, activeUrl: () => string|null}}
 */
export function addTileLayers(map, { tileLayers, slopeLayer: slopeSpec }) {
  const layers = tileLayers.map((spec) => [spec, L.tileLayer(spec.url, spec)]);
  const slopeLayer = L.tileLayer(slopeSpec.url, slopeSpec);

  const [[defaultSpec, defaultLayer]] = layers;
  defaultLayer.addTo(map);
  let active = defaultSpec;

  L.control
    .layers(
      Object.fromEntries(layers.map(([spec, layer]) => [spec.label, layer])),
      { [slopeSpec.label]: slopeLayer },
    )
    .addTo(map);

  map.on("baselayerchange", (e) => {
    active = e.layer.options;
    console.log("Layer changed to:", active.name);
  });

  return { slopeLayer, activeUrl: () => active.url ?? null };
}

/**
 * A colour key for the slope overlay, visible only while the overlay is on.
 *
 * @param {L.Map} map
 * @param {{slopeRanges: Array<{angle: string, color: string}>, slopeLayer: object}} settings
 */
export function addSlopeLegend(map, { slopeRanges, slopeLayer }) {
  const legend = new (L.Control.extend({
    options: { position: "bottomleft" },
    onAdd() {
      const container = L.DomUtil.create("div", "slope-legend leaflet-bar leaflet-control");
      const row = L.DomUtil.create("div", "slope-legend-container", container);
      for (const { angle, color } of slopeRanges) {
        const item = L.DomUtil.create("div", "slope-legend-item", row);
        item.style.backgroundColor = color;
        item.textContent = angle;
      }
      return container;
    },
  }))();

  legend.addTo(map);

  const setVisible = (visible) => (e) => {
    if (e.name === slopeLayer.label) {
      legend.getContainer().style.display = visible ? "block" : "none";
    }
  };
  map.on("overlayadd", setVisible(true));
  map.on("overlayremove", setVisible(false));

  return legend;
}

/**
 * Bivouac ("Kothe") markers, fetched once and shown from `minZoom` upwards.
 *
 * @param {L.Map} map
 * @param {{minZoom: number, iconUrl: string, iconSize: number[], endpoint: string}} biwak
 */
export function addBiwakLayer(map, { minZoom, iconUrl, iconSize, endpoint }) {
  const group = L.layerGroup();
  const icon = L.icon({ iconUrl, iconSize });

  fetch(endpoint)
    .then((r) => r.json())
    .then((points) => {
      for (const [lat, lon] of points) L.marker([lat, lon], { icon }).addTo(group);
    })
    .catch((error) => console.error("Failed to load bivouacs:", error));

  map.on("zoomend", () => {
    const shouldShow = map.getZoom() >= minZoom;
    if (shouldShow !== map.hasLayer(group)) {
      shouldShow ? map.addLayer(group) : map.removeLayer(group);
    }
  });

  return group;
}

/** Address search; drops a marker wherever a result is picked. */
export function addGeocoder(map) {
  const control = L.Control.geocoder({ defaultMarkGeocode: true }).addTo(map);
  control.setPosition("topleft");
  control.on("markgeocode", (e) => L.marker(e.geocode.center).addTo(map));
  return control;
}
