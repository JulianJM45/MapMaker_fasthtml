/**
 * The geometry modules must behave exactly like the pre-refactor script.
 *
 * Every assertion here is `strictEqual` on doubles: the refactor kept the
 * original operator grouping precisely so that no rectangle can ever land on a
 * different coordinate than it used to.
 */

import assert from "node:assert/strict";
import test from "node:test";

import {
  EQUATORIAL_CIRCUMFERENCE,
  POLAR_CIRCUMFERENCE,
  aspectRatio,
  boundsFromMeters,
  fitAspectRatio,
  metersFromBounds,
  pageMeters,
} from "../../static/js/geo.js";
import {
  editedRectangleMeters,
  getBoundsFromMeters,
  getMetersFromBounds,
  newRectangleMeters,
  seededRandom,
  stubBounds,
} from "./legacy.mjs";

const DEFAULTS = { width: 288, height: 201, scale: 25000 };

test("earth constants match the original script", () => {
  assert.equal(POLAR_CIRCUMFERENCE, 40007863);
  assert.equal(EQUATORIAL_CIRCUMFERENCE, 40075016.686);
});

test("boundsFromMeters is identical to the legacy implementation", () => {
  const random = seededRandom(1);
  for (let i = 0; i < 2000; i++) {
    const center = { lat: random() * 150 - 75, lng: random() * 360 - 180 };
    const widthMeters = random() * 200000 + 1;
    const heightMeters = random() * 200000 + 1;

    const actual = boundsFromMeters(center, widthMeters, heightMeters);
    const expected = getBoundsFromMeters(
      stubBounds({ north: center.lat, south: center.lat, east: center.lng, west: center.lng }),
      widthMeters,
      heightMeters,
    );

    assert.equal(actual.north, expected.getNorth());
    assert.equal(actual.south, expected.getSouth());
    assert.equal(actual.east, expected.getEast());
    assert.equal(actual.west, expected.getWest());
  }
});

test("metersFromBounds is identical to the legacy implementation", () => {
  const random = seededRandom(2);
  for (let i = 0; i < 2000; i++) {
    const south = random() * 150 - 75;
    const west = random() * 350 - 180;
    const bounds = { south, west, north: south + random() * 2, east: west + random() * 2 };

    const actual = metersFromBounds(bounds);
    const [widthMeters, heightMeters] = getMetersFromBounds(stubBounds(bounds));

    assert.equal(actual.widthMeters, widthMeters);
    assert.equal(actual.heightMeters, heightMeters);
  }
});

test("boundsFromMeters and metersFromBounds round-trip", () => {
  const bounds = boundsFromMeters({ lat: 48.15, lng: 11.59 }, 7200, 5025);
  const { widthMeters, heightMeters } = metersFromBounds(bounds);

  // The width is measured at the mid-latitude it was built from, so this is
  // exact up to floating point noise rather than merely approximate.
  assert.ok(Math.abs(widthMeters - 7200) < 1e-6, `width ${widthMeters}`);
  assert.ok(Math.abs(heightMeters - 5025) < 1e-6, `height ${heightMeters}`);
});

test("pageMeters matches the legacy rectangle sizing, both orientations", () => {
  for (const orientation of ["landscape", "portrait"]) {
    for (const scale of [5000, 25000, 50000]) {
      const config = { ...DEFAULTS, scale, orientation };
      const { widthMeters, heightMeters } = pageMeters(config);
      const [legacyWidth, legacyHeight] = newRectangleMeters(config);

      assert.equal(widthMeters, legacyWidth);
      assert.equal(heightMeters, legacyHeight);
    }
  }
});

test("a landscape page at 1:25000 covers 7.2 x 5.025 km", () => {
  assert.deepEqual(pageMeters({ ...DEFAULTS, orientation: "landscape" }), {
    widthMeters: 7200,
    heightMeters: 5025,
  });
  assert.deepEqual(pageMeters({ ...DEFAULTS, orientation: "portrait" }), {
    widthMeters: 5025,
    heightMeters: 7200,
  });
});

test("fitAspectRatio is identical to the legacy edit handler", () => {
  const random = seededRandom(3);
  const ratios = [288 / 201, 201 / 288, 1, 2, 0.5];

  for (const configRatio of ratios) {
    for (let i = 0; i < 2000; i++) {
      const widthMeters = random() * 50000 + 1;
      const heightMeters = random() * 50000 + 1;

      const actual = fitAspectRatio(widthMeters, heightMeters, configRatio);
      const [legacyWidth, legacyHeight] = editedRectangleMeters(
        widthMeters,
        heightMeters,
        configRatio,
      );

      assert.equal(actual.widthMeters, legacyWidth);
      assert.equal(actual.heightMeters, legacyHeight);
    }
  }
});

test("fitAspectRatio never shrinks the dragged rectangle", () => {
  const random = seededRandom(4);
  const configRatio = aspectRatio(DEFAULTS);

  for (let i = 0; i < 1000; i++) {
    const widthMeters = random() * 50000 + 1;
    const heightMeters = random() * 50000 + 1;
    const fitted = fitAspectRatio(widthMeters, heightMeters, configRatio);

    assert.ok(fitted.widthMeters >= widthMeters - 1e-9);
    assert.ok(fitted.heightMeters >= heightMeters - 1e-9);
  }
});

test("fitAspectRatio keeps the orientation the drag leans towards", () => {
  const configRatio = aspectRatio(DEFAULTS); // landscape page

  const wide = fitAspectRatio(10000, 1000, configRatio);
  assert.ok(wide.widthMeters > wide.heightMeters, "wide drag stays landscape");
  assert.ok(Math.abs(wide.widthMeters / wide.heightMeters - configRatio) < 1e-9);

  const tall = fitAspectRatio(1000, 10000, configRatio);
  assert.ok(tall.heightMeters > tall.widthMeters, "tall drag stays portrait");
  assert.ok(Math.abs(tall.heightMeters / tall.widthMeters - configRatio) < 1e-9);
});

test("aspectRatio reads the unrotated page size", () => {
  assert.equal(aspectRatio({ width: 288, height: 201 }), 288 / 201);
});
