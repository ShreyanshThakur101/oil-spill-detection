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
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
        />

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
