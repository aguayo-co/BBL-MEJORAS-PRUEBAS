import * as L from "leaflet";
import { openModal } from "./components/c11_modal";

function processCoordinate(coordinate) {
  return parseFloat(coordinate.replace(",", "."));
}

function getBaseLayers() {
  var EsriWorldImagery = L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    {
      attribution:
        "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community"
    }
  );

  var OpenStreetMapMapnik = L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }
  );

  const baseLayers = {
    Satellite: EsriWorldImagery,
    Map: OpenStreetMapMapnik
  };

  return baseLayers;
}

function addMarkers(mapId, renderedMap) {
  document
    .querySelectorAll(`.ag-js-mapMilestone[data-map-id=${mapId}]`)
    .forEach(milestone => {
      const customIcon = new L.Icon({
        iconUrl: milestone.dataset.pingImageUrl
      });
      const marker = L.marker(
        [
          processCoordinate(milestone.dataset.latitude),
          processCoordinate(milestone.dataset.longitude)
        ],
        { icon: customIcon }
      ).addTo(renderedMap);
      marker._icon.setAttribute("data-modal", `modal-${milestone.id}`);
      marker._icon.addEventListener("keyup", function(event) {
        if (event.keyCode === 13) {
          event.preventDefault();
          openModal(this);
        }
      });
    });
}

function setImageOverlay(map, renderedMap) {
  const imageUrl = map.dataset.imageUrl;

  if (!imageUrl) {
    return;
  }

  const imageBounds = [
    [
      processCoordinate(map.dataset.imageTopCornerBoundLatitude),
      processCoordinate(map.dataset.imageTopCornerBoundLongitude)
    ],
    [
      processCoordinate(map.dataset.imageBottomCornerBoundLatitude),
      processCoordinate(map.dataset.imageBottomCornerBoundLongitude)
    ]
  ];
  L.imageOverlay(imageUrl, imageBounds).addTo(renderedMap);
}

document
  .getElementsByClassName("ag-js-expositionMapContainer")
  .forEach(mapContainer => {
    mapContainer.getElementsByClassName("ag-js-expositionMap").forEach(map => {
      map.style.height = "100%";
      const baseLayers = getBaseLayers();
      const renderedMap = L.map(map, {
        center: [
          processCoordinate(map.dataset.centerAtLatitude),
          processCoordinate(map.dataset.centerAtLongitude)
        ],
        zoom: map.dataset.minZoomLevel,
        minZoom: map.dataset.minZoomLevel,
        maxZoom: map.dataset.maxZoomLevel,
        layers: [baseLayers.Map, baseLayers.Satellite],
        gestureHandling: true
      });

      L.control.layers(baseLayers).addTo(renderedMap);
      addMarkers(map.id, renderedMap);
      setImageOverlay(map, renderedMap);
    });
  });
