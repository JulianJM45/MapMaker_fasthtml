/**
 * Geodesy for MapMaker's selection rectangles.
 *
 * Everything here is pure: bounds are plain `{north, south, east, west}`
 * objects in degrees and sizes are plain metres, so none of it needs Leaflet
 * (or a browser) to run -- see `tests/js/geo.test.mjs`.
 */

/** Earth's circumference through the poles, in metres. */
export const POLAR_CIRCUMFERENCE = 40007863;
/** Earth's circumference around the equator, in metres. */
export const EQUATORIAL_CIRCUMFERENCE = 40075016.686;

const toRadians = (degrees) => degrees * (Math.PI / 180);

/**
 * Bounds of a rectangle of the given ground size, centred on `center`.
 *
 * @param {{lat: number, lng: number}} center
 * @param {number} widthMeters
 * @param {number} heightMeters
 * @returns {{north: number, south: number, east: number, west: number}}
 */
export function boundsFromMeters(center, widthMeters, heightMeters) {
  const lngDeltaHalf =
    (widthMeters / 2 / (EQUATORIAL_CIRCUMFERENCE * Math.cos(toRadians(center.lat)))) * 360;
  const latDeltaHalf = (heightMeters / 2 / POLAR_CIRCUMFERENCE) * 360;

  return {
    north: center.lat + latDeltaHalf,
    south: center.lat - latDeltaHalf,
    east: center.lng + lngDeltaHalf,
    west: center.lng - lngDeltaHalf,
  };
}

/**
 * Ground size of a bounding box, measured across its mid-latitude.
 *
 * @param {{north: number, south: number, east: number, west: number}} bounds
 * @returns {{widthMeters: number, heightMeters: number}}
 */
export function metersFromBounds({ north, south, east, west }) {
  return {
    widthMeters:
      ((east - west) * (EQUATORIAL_CIRCUMFERENCE * Math.cos(toRadians((north + south) / 2)))) / 360,
    heightMeters: ((north - south) * POLAR_CIRCUMFERENCE) / 360,
  };
}

/**
 * Ground size covered by one printed page at the configured scale.
 *
 * `width`/`height` are the page size in millimetres; a portrait page simply
 * swaps them.
 *
 * @param {{width: number, height: number, scale: number, orientation: string}} config
 * @returns {{widthMeters: number, heightMeters: number}}
 */
export function pageMeters({ width, height, scale, orientation }) {
  const [mmWidth, mmHeight] = orientation === "portrait" ? [height, width] : [width, height];
  return {
    widthMeters: (mmWidth * scale) / 1000,
    heightMeters: (mmHeight * scale) / 1000,
  };
}

/** Page aspect ratio (width / height) of a configuration. */
export const aspectRatio = ({ width, height }) => width / height;

/**
 * Grow a freshly dragged rectangle onto the page's aspect ratio.
 *
 * The orientation the user dragged towards wins: drag wide and you get a
 * landscape page, drag tall and the page ratio is flipped for you. The result
 * never shrinks below the drag, so the selection always covers what was drawn.
 *
 * @param {number} widthMeters   dragged width
 * @param {number} heightMeters  dragged height
 * @param {number} configRatio   page width / height, see {@link aspectRatio}
 * @returns {{widthMeters: number, heightMeters: number}}
 */
export function fitAspectRatio(widthMeters, heightMeters, configRatio) {
  const wantsLandscape = widthMeters / heightMeters > 1;
  // True when the page's own orientation already matches the drag, i.e. when
  // `configRatio` can be used as-is instead of flipped.
  const matchesPage = wantsLandscape ? configRatio >= 1 : configRatio <= 1;

  if (wantsLandscape) {
    const width = matchesPage
      ? Math.max(widthMeters, heightMeters * configRatio)
      : Math.max(widthMeters, heightMeters / configRatio);
    return {
      widthMeters: width,
      heightMeters: matchesPage ? width / configRatio : width * configRatio,
    };
  }

  const height = matchesPage
    ? Math.max(heightMeters, widthMeters / configRatio)
    : Math.max(heightMeters, widthMeters * configRatio);
  return {
    widthMeters: matchesPage ? height * configRatio : height / configRatio,
    heightMeters: height,
  };
}
