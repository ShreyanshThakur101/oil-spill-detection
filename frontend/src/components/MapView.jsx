import React, { useEffect } from "react";
import { MapContainer, TileLayer, LayersControl, useMap } from "react-leaflet";
import L from "leaflet";
import SlickLayer from "./SlickLayer";
import DriftLayer from "./DriftLayer";
import AISTrackLayer from "./AISTrackLayer";
import ICGCuttersLayer from "./ICGCuttersLayer";

function AutoFitBounds({ detection, drift, vessels }) {
  const map = useMap();

  useEffect(() => {
    if (!detection && !drift && (!vessels || vessels.length === 0)) return;
    try {
      const group = L.featureGroup();
      if (detection?.polygon_geojson) {
        group.addLayer(L.geoJSON(detection.polygon_geojson));
      }
      if (drift?.origin_polygon_geojson) {
        group.addLayer(L.geoJSON(drift.origin_polygon_geojson));
      }
      if (vessels && vessels.length > 0) {
        vessels.forEach((v) => {
          if (v.track_geojson) {
            group.addLayer(L.geoJSON(v.track_geojson));
          }
        });
      }
      const bounds = group.getBounds();
      if (bounds.isValid()) {
        map.fitBounds(bounds, { padding: [50, 50], maxZoom: 11 });
      }
    } catch (e) {
      // Fallback
    }
  }, [detection, drift, vessels, map]);

  return null;
}

export default function MapView({
  caseId = 1,
  detection,
  drift,
  vessels,
  selectedMmsi,
  onSelectVessel,
}) {
  // Center for Kochi (Case 1) vs Mumbai (Case 2)
  const center = caseId === 2 ? [18.82, 72.65] : [9.65, 76.05];
  const zoom = 9;

  return (
    <div className="map-wrapper">
      <MapContainer center={center} zoom={zoom} className="leaflet-map" scrollWheelZoom={true}>
        <AutoFitBounds detection={detection} drift={drift} vessels={vessels} />

        <LayersControl position="topright">
          <LayersControl.BaseLayer checked name="Dark Marine Canvas (Radar Optimised)">
            <TileLayer
              attribution="Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ"
              url="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}"
              maxZoom={16}
            />
          </LayersControl.BaseLayer>

          <LayersControl.BaseLayer name="Ocean Basemap & Bathymetry (GEBCO/Esri)">
            <TileLayer
              attribution="Tiles &copy; Esri &mdash; GEBCO, NOAA, CHS"
              url="https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean/MapServer/tile/{z}/{y}/{x}"
              maxZoom={13}
            />
          </LayersControl.BaseLayer>

          <LayersControl.BaseLayer name="Satellite Optical Imagery (Esri)">
            <TileLayer
              attribution="Tiles &copy; Esri &mdash; Maxar, Earthstar Geographics"
              url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
              maxZoom={18}
            />
          </LayersControl.BaseLayer>

          <LayersControl.BaseLayer name="OpenStreetMap Standard">
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              maxZoom={19}
            />
          </LayersControl.BaseLayer>

          {/* Overlays */}
          <LayersControl.Overlay checked name="Lagrangian Particles (200 Particles)">
            {drift && (
              <DriftLayer
                originGeojson={drift.origin_polygon_geojson}
                particlesGeojson={drift.particle_cloud_geojson}
                trajectoriesGeojson={drift.particle_trajectories_geojson}
              />
            )}
          </LayersControl.Overlay>

          <LayersControl.Overlay checked name="Sentinel-1 SAR Slick Mask (U-Net)">
            {detection && (
              <SlickLayer
                geojson={detection.polygon_geojson}
                areaKm2={detection.shape_features?.area_km2}
                confidence={detection.confidence}
              />
            )}
          </LayersControl.Overlay>

          <LayersControl.Overlay checked name="AIS Telemetry & Blackout Gaps">
            {vessels && (
              <AISTrackLayer
                vessels={vessels}
                selectedMmsi={selectedMmsi}
                onSelectVessel={onSelectVessel}
              />
            )}
          </LayersControl.Overlay>

          <LayersControl.Overlay checked name="Indian Coast Guard Cutters & 12NM Sea Limit">
            <ICGCuttersLayer caseId={caseId} />
          </LayersControl.Overlay>
        </LayersControl>
      </MapContainer>

      {/* Geospatial Map Legend */}
      <div className="map-legend">
        <div className="legend-header">SAGAR-DRISHTI Multi-Layer Explorer</div>
        <div className="legend-grid">
          <div className="legend-item">
            <span className="legend-symbol legend-slick"></span>
            <span>SAR Slick (U-Net)</span>
          </div>
          <div className="legend-item">
            <span className="legend-symbol legend-drift"></span>
            <span>Origin Cone (-18h)</span>
          </div>
          <div className="legend-item">
            <span className="legend-symbol legend-particles"></span>
            <span>200 Virtual Particles</span>
          </div>
          <div className="legend-item">
            <span className="legend-symbol legend-ais"></span>
            <span>AIS Vessel Tracks</span>
          </div>
          <div className="legend-item">
            <span className="legend-symbol legend-blackout"></span>
            <span>Deliberate AIS Blackout</span>
          </div>
          <div className="legend-item">
            <span className="legend-symbol legend-icg"></span>
            <span>ICG Response Cutter</span>
          </div>
        </div>
      </div>
    </div>
  );
}
