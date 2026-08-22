/**
 * MapMaker frontend entry point.
 *
 * Everything that is *not* Leaflet lives elsewhere: page defaults and the
 * current configuration in `settings.js`, the rectangle geometry in `geo.js`,
 * the download round-trip in `download.js`. Opening the configuration panel,
 * the format/orientation switches and the AutoZoom blur are handled entirely
 * by markup and CSS -- see `modules/ui.py` and `static/styles.css`.
 */

import { buildPayload, requestMap, saveBlob } from "./download.js";
import {
  aspectRatio,
  boundsFromMeters,
  fitAspectRatio,
  metersFromBounds,
  pageMeters,
} from "./geo.js";
import { addBiwakLayer, addGeocoder, addSlopeLegend, addTileLayers } from "./layers.js";
import { readConfig, readSettings } from "./settings.js";

const byId = (id) => document.getElementById(id);

/** Attach a listener, tolerating elements that are not on the page. */
const on = (id, event, handler) => byId(id)?.addEventListener(event, handler);

const toLatLngBounds = ({ north, south, east, west }) =>
  L.latLngBounds(L.latLng(south, west), L.latLng(north, east));

const fromLatLngBounds = (bounds) => ({
  north: bounds.getNorth(),
  south: bounds.getSouth(),
  east: bounds.getEast(),
  west: bounds.getWest(),
});

function main() {
  const settings = readSettings();
  const config = () => readConfig(settings.defaults);

  const map = L.map("map").setView(settings.mapStart.center, settings.mapStart.zoom);
  const { slopeLayer, activeUrl } = addTileLayers(map, settings);
  addSlopeLegend(map, settings);
  addBiwakLayer(map, settings.biwak);
  addGeocoder(map);

  const log = byId("log");
  const showMessage = (message) => log && (log.innerText = message);

  // --- drawing -------------------------------------------------------------
  const editableLayers = new L.FeatureGroup().addTo(map);
  const rectangles = [];

  map.addControl(
    new L.Control.Draw({
      draw: {
        rectangle: true,
        marker: true,
        polyline: false,
        circle: false,
        polygon: false,
        circlemarker: false,
      },
      edit: { featureGroup: editableLayers, edit: true, remove: true },
    }),
  );

  /** Re-shape a rectangle to a ground size, keeping its centre. */
  const resize = (rectangle, widthMeters, heightMeters) => {
    const center = rectangle.getBounds().getCenter();
    rectangle.setBounds(toLatLngBounds(boundsFromMeters(center, widthMeters, heightMeters)));
  };

  map.on("draw:created", ({ layer, layerType }) => {
    editableLayers.addLayer(layer);
    if (layerType !== "rectangle") return;

    // A drawn rectangle is snapped to exactly one page at the current scale...
    const { widthMeters, heightMeters } = pageMeters(config());
    resize(layer, widthMeters, heightMeters);
    rectangles.push(layer);

    // ...and resizing it keeps that page's aspect ratio, in whichever
    // orientation the drag leans towards.
    layer.on("edit", () => {
      const dragged = metersFromBounds(fromLatLngBounds(layer.getBounds()));
      const fitted = fitAspectRatio(
        dragged.widthMeters,
        dragged.heightMeters,
        aspectRatio(config()),
      );
      resize(layer, fitted.widthMeters, fitted.heightMeters);
    });
  });

  // --- panel controls ------------------------------------------------------
  on("showZoomLevel", "click", () => map.setZoom(config().zoom));

  on("gpxFileInput", "change", (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.addEventListener("load", () =>
      new L.GPX(reader.result, { async: true })
        .on("loaded", ({ target }) => map.fitBounds(target.getBounds()))
        .addTo(map),
    );
    reader.readAsText(file);
  });

  // --- download ------------------------------------------------------------
  on("download-button", "click", async (event) => {
    event.preventDefault();
    log?.classList.add("log-active");
    // Get the settings panel out of the way of the progress log.
    const configureToggle = byId("configure-toggle");
    if (configureToggle) configureToggle.checked = false;

    const markers = [];
    editableLayers.eachLayer((layer) => {
      if (layer instanceof L.Marker) markers.push(layer.getLatLng());
    });

    const payload = buildPayload({
      rectangles: rectangles
        .filter((r) => editableLayers.hasLayer(r))
        .map((r) => fromLatLngBounds(r.getBounds())),
      markers,
      tileUrl: activeUrl(),
      slope: map.hasLayer(slopeLayer),
      config: config(),
    });

    try {
      const { blob, filename } = await requestMap(settings.endpoints.render, payload);
      saveBlob(blob, filename);
      showMessage("Map downloaded successfully!");
    } catch (error) {
      console.error("Error:", error);
      showMessage("An error occurred while sending the coordinates.");
    } finally {
      log?.classList.remove("log-active");
    }
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", main);
} else {
  main();
}
