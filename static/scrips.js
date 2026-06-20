// ====== CONSTANTS & CONFIGURATION ======
const GEO_CONSTANTS = {
  POL_CF: 40007863,
  ECF: 40075016.686,
};
const slopeRanges = [
  { angle: "30°", color: "rgba(255, 255, 0, 0.6)" },
  { angle: "35°", color: "rgba(255, 165, 0, 0.6)" },
  { angle: "40°", color: "rgba(255, 0, 0, 0.6)" },
  { angle: "45°", color: "rgba(128, 0, 128, 0.6)" },
];

// ====== UTILITY FUNCTIONS ======
function addEventListeners(elementConfigs) {
  elementConfigs.forEach(({ id, event, handler }) => {
    const element = document.getElementById(id);
    if (element) {
      element.addEventListener(event, handler);
    }
  });
}

// ====== CLASSES ======
class ToggleButton {
  constructor(leftId, rightId, btnId, defaultLeft = true) {
    this.left = document.getElementById(leftId);
    this.right = document.getElementById(rightId);
    this.btn = document.getElementById(btnId);
    this.default = defaultLeft;
    // Set initial position based on defaultLeft
    if (this.btn) {
      this.btn.style.left = defaultLeft ? "0%" : "50%";
      this.btn.style.display = "block";
    }
  }

  setLeft(callback) {
    if (this.left && this.right && this.btn) {
      this.left.addEventListener("click", () => {
        this.btn.style.left = "0%";
        this.isLeft = true;
        callback(true);
      });
    }
  }

  setRight(callback) {
    if (this.left && this.right && this.btn) {
      this.right.addEventListener("click", () => {
        this.btn.style.left = "50%";
        this.isLeft = false;
        callback(false);
      });
    }
  }
}

// ====== MAIN INITIALIZATION ======
document.addEventListener("DOMContentLoaded", function () {
  var map = L.map("map").setView([48.149972, 11.590917], 7);
  // var map = L.map("map").setView([47.429444, 11.0475], 13);

  var openStreetMapLayer = L.tileLayer(
    "https://a.tile.openstreetmap.de/{z}/{x}/{y}.png",
    {
      name: "a.tile.openstreetmap.de",
      attribution:
        '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
    },
  );
  var openTopoMapLayer = L.tileLayer(
    "https://a.tile.opentopomap.org/{z}/{x}/{y}.png",
    {
      name: "a.tile.opentopomap.org",
      attribution:
        '&copy; <a href="https://opentopomap.org">OpenTopoMap</a> contributors',
    },
  );
  var outdooractiveLayer = L.tileLayer(
    "https://t0.outdooractive.com/portal/map/{z}/{x}/{y}.png",
    {
      name: "t0.outdooractive.com/portal/map",
      attribution:
        '&copy; <a href="https://www.outdooractive.com">Outdooractive</a> contributors',
    },
  );
  var tracesTrackLayer = L.tileLayer(
    "https://tile.tracestrack.com/topo_en/{z}/{x}/{y}.webp?key=0cf0393c74ee7d4cd976c5cd9f891d60",
    {
      name: "tile.tracestrack.com/topo_en",
      attribution:
        '&copy; <a href="https://www.tracestrack.com">Tracestrack</a> contributors',
    },
  );
  var mapyLayer = L.tileLayer(
    "https://api.mapy.com/v1/maptiles/outdoor/256@2x/{z}/{x}/{y}?apikey=pLSF5p9ls6uM9fXmmsMieCw0YGl6BC6AERrtMcFLgU0",
    {
      name: "api.mapy.com/v1/maptiles/outdoor",
      attribution:
        'a href="https://api.mapy.com/copyright" target="_blank">&copy; Seznam.cz a.s. a další</a>',
    },
  );
  var bergfexLayer = L.tileLayer(
    "https://tiles.bergfex.at/styles/bergfex-osm/{z}/{x}/{y}.jpg",
    {
      name: "tiles.bergfex.at/styles/bergfex-osm",
      attribution:
        '&copy; <a href="https://www.bergfex.at">Bergfex</a> contributors',
    },
  );
  var bergfexSlopeLayer = L.tileLayer(
    "https://tiles.bergfex.at/data/europe-slope-11-15/{z}/{x}/{y}.png",
    {
      name: "tiles.bergfex.at/data/europe-slope-11-15",
      attribution:
        '&copy; <a href="https://www.bergfex.at">Bergfex</a> contributors',
      opacity: 0.4,
    },
  );

  // Add default layer
  openStreetMapLayer.addTo(map);

  // Create a layer control and add it to the map
  var baseMaps = {
    OpenStreetMap: openStreetMapLayer,
    "⭐ Mapy": mapyLayer,
    OpenTopoMap: openTopoMapLayer,
    Outdooractive: outdooractiveLayer,
    Tracestrack: tracesTrackLayer,
    Bergfex: bergfexLayer,
  };

  var overlayMaps = {
    "Slope Overlay": bergfexSlopeLayer,
  };

  L.control.layers(baseMaps, overlayMaps).addTo(map);

  // Track layer changes
  var layer_name = "a.tile.openstreetmap.de";

  map.on("baselayerchange", function (e) {
    layer_name = e.layer.options.name;
    console.log("Layer changed to:", layer_name);
  });

  // Create slope legend control
  var SlopeLegend = L.Control.extend({
    options: {
      position: "bottomleft",
    },

    onAdd: function (map) {
      var container = L.DomUtil.create(
        "div",
        "slope-legend leaflet-bar leaflet-control",
      );

      // Build the legend HTML
      var html = '<div style="display: flex; gap: 2px;">';

      slopeRanges.forEach(function (range) {
        html +=
          '<div class="slope-legend-item" style="background-color: ' +
          range.color +
          '">' +
          range.angle +
          "</div>";
      });

      html += "</div>";
      container.innerHTML = html;

      return container;
    },
  });

  var slopeLegend = new SlopeLegend();
  slopeLegend.addTo(map);

  // Show/hide slope legend when slope overlay is toggled
  map.on("overlayadd", function (e) {
    if (e.name === "Slope Overlay") {
      slopeLegend.getContainer().style.display = "block";
    }
  });

  map.on("overlayremove", function (e) {
    if (e.name === "Slope Overlay") {
      slopeLegend.getContainer().style.display = "none";
    }
  });

  // #2 log output
  function showMessage(message) {
    // console.log(message);
    document.getElementById("log").innerText = message;
  }
  // showMessage("Hello, World!");
  document.getElementById("log").style.zIndex = "0";

  // #3 map tools

  // Create a search control and add it to the map
  var searchControl = L.Control.geocoder({
    defaultMarkGeocode: true,
  }).addTo(map);
  searchControl.setPosition("topleft");

  // Event handler for when a location is found
  searchControl.on("markgeocode", function (e) {
    var latlng = e.geocode.center; // Get the coordinates of the search result
    var marker = L.marker(latlng).addTo(map); // Add a marker to the found location
  });

  // Initialize Leaflet.draw and Leaflet.Editable
  var editableLayers = new L.FeatureGroup(); // Create a feature group for editable layers
  map.addLayer(editableLayers);

  var drawOptions = {
    draw: {
      rectangle: true,
      polyline: false,
      circle: false,
      polygon: false,
      marker: true,
      circlemarker: false,
    },
    edit: {
      featureGroup: editableLayers, // Add the editable features to the map
      edit: true, // Enable editing
      remove: true, // Enable deleting
    },
  };

  var drawControl = new L.Control.Draw(drawOptions);
  map.addControl(drawControl);

  // load GPX track
  var gpxFileInput = document.getElementById("gpxFileInput");

  addEventListeners([
    {
      id: "gpxButton",
      event: "click",
      handler: () => gpxFileInput.click(),
    },
  ]);

  gpxFileInput.addEventListener("change", function (e) {
    var file = e.target.files[0];
    var reader = new FileReader();
    reader.addEventListener("load", function (e) {
      var gpxData = e.target.result;
      new L.GPX(gpxData, { async: true })
        .on("loaded", function (e) {
          map.fitBounds(e.target.getBounds());
        })
        .addTo(map);
    });
    reader.readAsText(file);
  });

  // #4 configuration

  // toggle configuration form
  function setupConfigurationToggle() {
    const configureButton = document.getElementById("configure-button");
    const configurationForm = document.getElementById("configuration-form");

    if (!configureButton || !configurationForm) {
      return;
    }

    configureButton.addEventListener("click", function (e) {
      e.preventDefault();

      // Check if form is currently visible
      const isVisible =
        !configurationForm.classList.contains("hide") &&
        (configurationForm.classList.contains("show") ||
          window.getComputedStyle(configurationForm).display !== "none");

      if (isVisible) {
        configurationForm.classList.remove("show");
        configurationForm.classList.add("hide");
      } else {
        configurationForm.classList.remove("hide");
        configurationForm.classList.add("show");
        // Reinitialize toggle buttons when form becomes visible
        setTimeout(initializeToggleButtons, 50);
      }
    });
  }

  // Setup configuration toggle
  setupConfigurationToggle();

  // get elements safely
  const elementIds = {
    scaleInput: "scale",
    autoZoomCheckbox: "AutoZoom",
    zoomLabel: "zoomLabel",
    zoomInput: "zoom",
    showZoomLevelButton: "showZoomLevel",
  };

  const elements = {};

  // Get elements safely
  Object.entries(elementIds).forEach(([key, id]) => {
    const element = document.getElementById(id);
    if (element) {
      elements[key] = element;
    }
  });

  // Initialize config using Python DEFAULT_CONFIG as fallback
  function getConfigFromForm() {
    // Use Python config as fallback if window.DEFAULT_CONFIG exists
    const defaultConfig = window.DEFAULT_CONFIG || {
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

  let config = getConfigFromForm();

  // Apply the blur effect by default (only to existing elements)
  ["zoomLabel", "zoomInput", "showZoomLevelButton"].forEach((id) => {
    const element = document.getElementById(id);
    if (element) {
      element.style.filter = "blur(2px)";
    }
  });

  // switch button functions (moved inline to toggle button initialization)

  // Show the current zoom level
  function showZoomLevel() {
    const z = parseInt(document.getElementById("zoom").value);
    map.setZoom(z);
  }

  // Update configuration function
  function updateConfiguration() {
    // Re-read config from form elements (syncs with Python DEFAULT_CONFIG)
    config = getConfigFromForm();
  }

  // Add event listeners only to existing elements
  ["scaleInput", "zoomInput"].forEach((key) => {
    if (elements[key]) {
      elements[key].addEventListener("input", updateConfiguration);
    }
  });
  ["autoZoomCheckbox"].forEach((key) => {
    if (elements[key]) {
      elements[key].addEventListener("change", updateConfiguration);
    }
  });
  if (elements.showZoomLevelButton) {
    elements.showZoomLevelButton.addEventListener("click", showZoomLevel);
  }

  if (elements.autoZoomCheckbox) {
    elements.autoZoomCheckbox.addEventListener("change", function () {
      const isAutoZoom = this.checked;
      ["zoomInput", "showZoomLevelButton", "zoomLabel"].forEach((key) => {
        if (elements[key]) {
          elements[key].disabled = isAutoZoom;
          elements[key].style.filter = isAutoZoom ? "blur(2px)" : "none";
        }
      });
    });
  }
  // Toggle button event listeners
  function initializeToggleButtons() {
    setTimeout(() => {
      // PDF/PNG toggle (left=PNG, right=PDF)
      const pdfToggle = new ToggleButton(
        "leftButton",
        "rightButton",
        "btn",
        false,
      );
      pdfToggle.setLeft(() => {
        console.log("Left button clicked - PNG mode");
        config.pdf = false;
      });
      pdfToggle.setRight(() => {
        console.log("Right button clicked - PDF mode");
        config.pdf = true;
      });

      // Portrait/Landscape toggle (left=portrait, right=landscape)
      const orientationToggle = new ToggleButton(
        "portraitButton",
        "landscapeButton",
        "orientationBtn",
        false,
      );
      orientationToggle.setLeft(() => {
        console.log("Portrait clicked");
        config.orientation = "portrait";
      });
      orientationToggle.setRight(() => {
        console.log("Landscape clicked");
        config.orientation = "landscape";
      });
    }, 100);
  }
  // Initialize toggle buttons (try multiple times)
  initializeToggleButtons();

  // #5 create rectangles
  function getBoundsFromMeters(bounds, widthMeters, heightMeters) {
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
    const southWest = L.latLng(
      centerLat - latDeltaHalf,
      centerLng - lngDeltaHalf,
    );
    const northEast = L.latLng(
      centerLat + latDeltaHalf,
      centerLng + lngDeltaHalf,
    );

    return L.latLngBounds(southWest, northEast);
  }

  function getMetersFromBounds(bounds) {
    const North = bounds.getNorth();
    const South = bounds.getSouth();
    const East = bounds.getEast();
    const West = bounds.getWest();
    const widthMeters =
      ((East - West) *
        (GEO_CONSTANTS.ECF *
          Math.cos(((North + South) / 2) * (Math.PI / 180)))) /
      360;
    const heightMeters = ((North - South) * GEO_CONSTANTS.POL_CF) / 360;

    return [widthMeters, heightMeters];
  }

  var drawnRectangles = []; // Array to store drawn rectangles

  // draw rectangle
  map.on("draw:created", function (e) {
    var newRectangle = e.layer; // Store the new drawn rectangle

    // Set the rectangle to the fixed size
    var bounds = newRectangle.getBounds();

    // Apply orientation - swap width/height for portrait
    var baseWidth = config.width;
    var baseHeight = config.height;

    if (config.orientation === "portrait") {
      baseWidth = config.height;
      baseHeight = config.width;
    }

    var widthMeters = (baseWidth * config.scale) / 1000;
    var heightMeters = (baseHeight * config.scale) / 1000;

    const fixedSizeBounds = getBoundsFromMeters(
      bounds,
      widthMeters,
      heightMeters,
    );
    newRectangle.setBounds(fixedSizeBounds);
    drawnRectangles.push(newRectangle);
    // Add the rectangle to the editable feature group
    editableLayers.addLayer(newRectangle);

    // # edit rectangles with landscape/portrait switching
    newRectangle.on("edit", function (e) {
      var bounds = newRectangle.getBounds();
      var [widthMeters, heightMeters] = getMetersFromBounds(bounds);

      // Calculate the base aspect ratio from config
      var configRatio = config.width / config.height;
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
          targetHeightMeters = Math.max(
            heightMeters,
            widthMeters / configRatio,
          );
          targetWidthMeters = targetHeightMeters * configRatio;
        } else {
          // Config is landscape, flip it for portrait
          targetHeightMeters = Math.max(
            heightMeters,
            widthMeters * configRatio,
          );
          targetWidthMeters = targetHeightMeters / configRatio;
        }
      }

      const fixedSizeBounds = getBoundsFromMeters(
        bounds,
        targetWidthMeters,
        targetHeightMeters,
      );
      newRectangle.setBounds(fixedSizeBounds);
    });
  });

  // #6 send coordinates
  addEventListeners([
    {
      id: "download-button",
      event: "click",
      handler: (event) => {
        event.preventDefault();
        prepareAndSendData()
          .then((result) => {
            console.log("Data sent successfully:", result);
          })
          .catch((error) => {
            console.error("Failed to send data:", error);
          });
      },
    },
  ]);

  function prepareAndSendData() {
    document.getElementById("log").style.zIndex = "1000";
    document.getElementById("configuration-form").style.display = "none";
    // console.log("sending coordinates...");
    // showMessage("Sending coordinates...");

    // Iterate through the drawn rectangles and extract their coordinates
    var coordinates_List = [];
    drawnRectangles.forEach(function (rectangle) {
      if (editableLayers.hasLayer(rectangle)) {
        // Check if the rectangle is still active
        var bounds = rectangle.getBounds();
        var NorthWest = bounds.getNorthWest();
        var SouthEast = bounds.getSouthEast();

        var coordinates = {
          Northwest: [NorthWest.lat, NorthWest.lng],
          SouthEast: [SouthEast.lat, SouthEast.lng],
        };
        coordinates_List.push(coordinates);
      }
    });

    // Get the currently selected tile layer (exclude overlay layers like slope)
    var selectedTileLayer = null;
    var slopeLayerActive = false;

    // Iterate through all tile layers added to the map
    map.eachLayer(function (layer) {
      if (layer instanceof L.TileLayer && map.hasLayer(layer)) {
        // Check if the layer is an instance of L.TileLayer and is currently active
        if (layer.options && layer.options.name) {
          // Check if this is the slope overlay layer
          if (layer.options.opacity === 0.4) {
            slopeLayerActive = true;
          } else {
            // This is a base layer
            selectedTileLayer = layer._url;
          }
        }
      }
    });

    // Prepare the data to be sent
    var data = {
      coordinates_list: coordinates_List,
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

    return sendData(data);
  }

  function sendData(data) {
    // Send the data to the FastHTML backend using fetch
    return fetch("/send_coordinates", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    })
      .then((response) => {
        console.log("Response status:", response.status);
        console.log("Response headers:", [...response.headers.entries()]);

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Get filename from Content-Disposition header
        const contentDisposition = response.headers.get("Content-Disposition");
        let filename = "MyMap.pdf";
        if (contentDisposition) {
          console.log("Content-Disposition header:", contentDisposition);
          const filenameMatch = contentDisposition.match(/filename="([^"]+)"/);
          if (filenameMatch) {
            filename = filenameMatch[1];
          }
        }

        console.log("Downloading file:", filename);
        return response.blob().then((blob) => ({ blob, filename }));
      })
      .then(({ blob, filename }) => {
        console.log("File received successfully, size:", blob.size, "bytes");

        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.style.display = "none";
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();

        // Cleanup
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        // console.log("Download initiated for:", filename);
        showMessage("Map downloaded successfully!");

        document.getElementById("log").style.zIndex = "0";
      })
      .catch((error) => {
        console.error("Error:", error);
        showMessage("An error occurred while sending the coordinates.");
      });
  }
});
