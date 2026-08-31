import React from "react";
import { MapContainer, TileLayer, LayersControl } from "react-leaflet";
import SlickLayer from "./SlickLayer";
import DriftLayer from "./DriftLayer";
import AISTrackLayer from "./AISTrackLayer";

export default function MapView({ detection, drift, vessels, selectedMmsi, onSelectVessel }) {
  const center = [9.55, 75.95];
  const zoom = 9;

  return (
    <div className="map-wrapper">
      <MapContainer center={center} zoom={zoom} className="leaflet-map" scrollWheelZoom={true}>
        <LayersControl position="topright">
          <LayersControl.BaseLayer checked name="OpenStreetMap">
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              maxZoom={19}
            />
          </LayersControl.BaseLayer>

          <LayersControl.BaseLayer name="Ocean Basemap (Esri)">
            <TileLayer
              attribution="Tiles &copy; Esri &mdash; Sources: GEBCO, NOAA, CHS, National Geographic, Esri"
              url="https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean/MapServer/tile/{z}/{y}/{x}"
              maxZoom={13}
            />
          </LayersControl.BaseLayer>

          <LayersControl.BaseLayer name="Satellite Imagery (Esri)">
            <TileLayer
              attribution="Tiles &copy; Esri &mdash; Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community"
              url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
              maxZoom={18}
            />
          </LayersControl.BaseLayer>
        </LayersControl>

        {drift && <DriftLayer geojson={drift.origin_polygon_geojson} />}
        {detection && <SlickLayer geojson={detection.polygon_geojson} />}
        {vessels && (
          <AISTrackLayer
            vessels={vessels}
            selectedMmsi={selectedMmsi}
            onSelectVessel={onSelectVessel}
          />
        )}
      </MapContainer>

      <div className="map-legend">
        <div className="legend-item">
          <span className="legend-color legend-slick"></span>
          <span>SAR Oil Slick (U-Net)</span>
        </div>
        <div className="legend-item">
          <span className="legend-color legend-drift"></span>
          <span>Origin Cloud (OpenDrift)</span>
        </div>
        <div className="legend-item">
          <span className="legend-color legend-ais"></span>
          <span>AIS Vessel Trajectories</span>
        </div>
      </div>
    </div>
  );
}
