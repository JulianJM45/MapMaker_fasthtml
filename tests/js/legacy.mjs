/**
 * Verbatim extracts of the pre-refactor `static/scrips.js`.
 *
 * These are *reference implementations*, not production code: the arithmetic,
 * branch order and even the operator grouping are copied unchanged from commit
 * 346f123 so the tests can assert bit-for-bit equality against the new modules.
 * Leaflet is replaced with the three trivial stubs below; nothing else differs.
 *
 * Do not "clean these up" -- their whole value is being untouched originals.
 */

const GEO_CONSTANTS = {
  POL_CF: 40007863,
  ECF: 40075016.686,
};

/** @returns a stand-in for `L.latLngBounds`, with the accessors we use. */
export const stubBounds = ({ north, south, east, west }) => ({
  getNorth: () => north,
  getSouth: () => south,
  getEast: () => east,
  getWest: () => west,
  getCenter: () => ({ lat: (north + south) / 2, lng: (east + west) / 2 }),
});

const L = {
  latLng: (lat, lng) => ({ lat, lng }),
  latLngBounds: (southWest, northEast) =>
    stubBounds({
      south: southWest.lat,
      west: southWest.lng,
      north: northEast.lat,
      east: northEast.lng,
    }),
};

// --- verbatim from scrips.js -------------------------------------------------

export function getBoundsFromMeters(bounds, widthMeters, heightMeters) {
  var centerLat = bounds.getCenter().lat;
  var centerLng = bounds.getCenter().lng;
  const latRadians = centerLat * (Math.PI / 180); // Convert latitude to radians
  const widthHalf = widthMeters / 2;
  const heightHalf = heightMeters / 2;

  // Calculate the change in longitude (degrees) for the given width in meters
  const lngDeltaHalf =
    (widthHalf / (GEO_CONSTANTS.ECF * Math.cos(latRadians))) * 360;

  // Calculate the change in latitude (degrees) for the given height in meters
  const latDeltaHalf = (heightHalf / GEO_CONSTANTS.POL_CF) * 360;

  // Calculate the new bounds
  const southWest = L.latLng(centerLat - latDeltaHalf, centerLng - lngDeltaHalf);
  const northEast = L.latLng(centerLat + latDeltaHalf, centerLng + lngDeltaHalf);

  return L.latLngBounds(southWest, northEast);
}

export function getMetersFromBounds(bounds) {
  const North = bounds.getNorth();
  const South = bounds.getSouth();
  const East = bounds.getEast();
  const West = bounds.getWest();
  const widthMeters =
    ((East - West) *
      (GEO_CONSTANTS.ECF * Math.cos(((North + South) / 2) * (Math.PI / 180)))) /
    360;
  const heightMeters = ((North - South) * GEO_CONSTANTS.POL_CF) / 360;

  return [widthMeters, heightMeters];
}

/** Body of the `draw:created` handler that sizes a freshly drawn rectangle. */
export function newRectangleMeters(config) {
  var baseWidth = config.width;
  var baseHeight = config.height;

  if (config.orientation === "portrait") {
    baseWidth = config.height;
    baseHeight = config.width;
  }

  var widthMeters = (baseWidth * config.scale) / 1000;
  var heightMeters = (baseHeight * config.scale) / 1000;
  return [widthMeters, heightMeters];
}

/** Body of the rectangle `edit` handler, minus the Leaflet calls. */
export function editedRectangleMeters(widthMeters, heightMeters, configRatio) {
  var currentRatio = widthMeters / heightMeters;

  // Determine if user wants landscape or portrait based on current drag
  var isLandscape = currentRatio > 1;

  // Calculate target dimensions based on orientation preference
  var targetWidthMeters, targetHeightMeters;

  if (isLandscape) {
    // User dragged to landscape - use landscape orientation
    if (configRatio >= 1) {
      // Config is already landscape or square
      targetWidthMeters = Math.max(widthMeters, heightMeters * configRatio);
      targetHeightMeters = targetWidthMeters / configRatio;
    } else {
      // Config is portrait, flip it for landscape
      targetWidthMeters = Math.max(widthMeters, heightMeters / configRatio);
      targetHeightMeters = targetWidthMeters * configRatio;
    }
  } else {
    // User dragged to portrait - use portrait orientation
    if (configRatio <= 1) {
      // Config is already portrait or square
      targetHeightMeters = Math.max(heightMeters, widthMeters / configRatio);
      targetWidthMeters = targetHeightMeters * configRatio;
    } else {
      // Config is landscape, flip it for portrait
      targetHeightMeters = Math.max(heightMeters, widthMeters * configRatio);
      targetWidthMeters = targetHeightMeters / configRatio;
    }
  }

  return [targetWidthMeters, targetHeightMeters];
}

/** `getConfigFromForm`, with the element lookup passed in. */
export function getConfigFromForm(elements, DEFAULT_CONFIG) {
  const defaultConfig = DEFAULT_CONFIG || {
    width: 288,
    height: 201,
    scale: 25000,
    zoom: 14,
    autoZoom: true,
    pdf: true,
  };

  return {
    width: defaultConfig.width,
    height: defaultConfig.height,
    scale: elements.scaleInput
      ? parseFloat(elements.scaleInput.value)
      : defaultConfig.scale,
    zoom: elements.zoomInput
      ? parseInt(elements.zoomInput.value)
      : defaultConfig.zoom,
    autoZoom: elements.autoZoomCheckbox
      ? elements.autoZoomCheckbox.checked
      : defaultConfig.autoZoom,
    pdf: defaultConfig.pdf,
    orientation: defaultConfig.orientation || "landscape",
  };
}

/** The request body assembled by `prepareAndSendData`. */
export function legacyPayload(
  rectangleBounds,
  markerLatLngs,
  selectedTileLayer,
  config,
  slopeLayerActive,
) {
  var coordinates_List = [];
  var marker_list = [];
  rectangleBounds.forEach(function (bounds) {
    var NorthWest = { lat: bounds.getNorth(), lng: bounds.getWest() };
    var SouthEast = { lat: bounds.getSouth(), lng: bounds.getEast() };

    var coordinates = {
      Northwest: [NorthWest.lat, NorthWest.lng],
      SouthEast: [SouthEast.lat, SouthEast.lng],
    };
    coordinates_List.push(coordinates);
  });

  markerLatLngs.forEach(function (latlng) {
    marker_list.push(latlng);
  });

  return {
    coordinates_list: coordinates_List,
    markerList: marker_list,
    config: {
      tileLayer: selectedTileLayer,
      width: config.width,
      height: config.height,
      scale: config.scale,
      zoom: config.zoom,
      autoZoom: config.autoZoom,
      upscale: config.upscale,
      overview: config.overview,
      pdf: config.pdf,
      slope: slopeLayerActive,
    },
  };
}

/** Deterministic PRNG so the fuzz cases are reproducible. */
export function seededRandom(seed = 42) {
  let state = seed >>> 0;
  return () => {
    state = (state * 1664525 + 1013904223) >>> 0;
    return state / 4294967296;
  };
}
