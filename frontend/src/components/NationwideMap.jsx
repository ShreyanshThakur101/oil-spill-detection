import React, { useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  LayersControl,
  Rectangle,
  CircleMarker,
  Tooltip,
  useMap,
} from "react-leaflet";
import { useDemo } from "../context/DemoContext";
import DemoLayers from "./DemoLayers";

const INDIA_BOUNDS = [
  [5.5, 67.5],
  [24.8, 97.5],
];
const INDIA_CENTER = [21.2, 82.0];

function FlyToBounds({ bounds, maxZoom = 9, trigger }) {
  const map = useMap();
  useEffect(() => {
    if (!bounds) return;
    map.fitBounds(
      [
        [bounds[1], bounds[0]],
        [bounds[3], bounds[2]],
      ],
      { padding: [36, 36], maxZoom }
    );
  }, [map, bounds, trigger, maxZoom]);
  return null;
}

function ResetIndiaView({ token }) {
  const map = useMap();
  useEffect(() => {
    if (token > 0) {
      map.fitBounds(INDIA_BOUNDS, { padding: [20, 20] });
    }
  }, [map, token]);
  return null;
}

export default function NationwideMap({ focusBounds, resetToken = 0 }) {
  const { regions, scenarios, selectedScenario, selectScenario } = useDemo();

  const zoneColor = (zone) => {
    if (zone.coast === "WEST") return "#38bdf8";
    if (zone.coast === "EAST") return "#06d6a0";
    return "#c084fc";
  };

  return (
    <div className="map-wrapper nationwide-map">
      <MapContainer
        center={INDIA_CENTER}
        zoom={5}
        minZoom={4}
        maxBounds={INDIA_BOUNDS}
        maxBoundsViscosity={0.6}
        className="leaflet-map"
        scrollWheelZoom
      >
        <LayersControl position="topright">
          <LayersControl.BaseLayer checked name="Dark Marine Canvas">
            <TileLayer
              attribution="Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ"
              url="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}"
              maxZoom={16}
            />
          </LayersControl.BaseLayer>

          <LayersControl.BaseLayer name="Ocean Basemap & Bathymetry">
            <TileLayer
              attribution="Tiles &copy; Esri &mdash; GEBCO, NOAA"
              url="https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean/MapServer/tile/{z}/{y}/{x}"
              maxZoom={13}
            />
          </LayersControl.BaseLayer>

          <LayersControl.BaseLayer name="Satellite Optical Imagery">
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

          <LayersControl.Overlay checked name={`Coastal Zones (${regions.length}) — provisional envelopes`}>
            {regions.map((zone) => (
              <Rectangle
                key={zone.id}
                bounds={[
                  [zone.bbox[1], zone.bbox[0]],
                  [zone.bbox[3], zone.bbox[2]],
                ]}
                pathOptions={{
                  color: zoneColor(zone),
                  weight: 1.4,
                  fillColor: zoneColor(zone),
                  fillOpacity: 0.07,
                  dashArray: "5 4",
                }}
              >
                <Tooltip sticky>
                  <strong>{zone.id} — {zone.name}</strong>
                  <br />
                  {zone.type === "STATE" ? "Coastal State" : "Coastal UT"} • {zone.coast}
                  <br />
                  Coastline: {zone.coastline_km} km
                  <br />
                  MRCC: {zone.primary_mrcc}
                  <br />
                  <em>Provisional search envelope — not a legal boundary</em>
                </Tooltip>
              </Rectangle>
            ))}
          </LayersControl.Overlay>

          <LayersControl.Overlay checked name="Case Study Markers (5)">
            {scenarios.map((scenario) => {
              if (!scenario.center) return null;
              const isSelected = scenario.id === selectedScenario;
              return (
                <CircleMarker
                  key={scenario.id}
                  center={scenario.center}
                  radius={isSelected ? 12 : 8}
                  pathOptions={{
                    color: isSelected ? "#ffd166" : "#00d2ff",
                    fillColor: isSelected ? "#ffd166" : "#0077b6",
                    fillOpacity: 0.9,
                    weight: 2,
                  }}
                  eventHandlers={{ click: () => selectScenario(scenario.id) }}
                >
                  <Tooltip direction="top" offset={[0, -8]}>
                    <strong>{scenario.name}</strong> — illustrative case study
                    <br />
                    {scenario.stats?.detections ?? 0} slick detections •{" "}
                    {scenario.stats?.incidents ?? 0} investigations
                  </Tooltip>
                </CircleMarker>
              );
            })}
          </LayersControl.Overlay>

          <LayersControl.Overlay checked name="Selected Case Study — Detections / Drift / Vessels / Investigations">
            <DemoLayers />
          </LayersControl.Overlay>
        </LayersControl>

        <FlyToBounds bounds={focusBounds} trigger={focusBounds?.join(",")} />
        <ResetIndiaView token={resetToken} />
      </MapContainer>

      <div className="map-legend">
        <div className="legend-header">National Intelligence Map</div>
        <div className="legend-grid">
          <div className="legend-item">
            <span className="legend-symbol legend-slick" />
            <span>Detection record</span>
          </div>
          <div className="legend-item">
            <span className="legend-symbol legend-drift" />
            <span>Drift origin envelope</span>
          </div>
          <div className="legend-item">
            <span className="legend-symbol legend-particles" />
            <span>Vessel attribution</span>
          </div>
          <div className="legend-item">
            <span className="legend-symbol legend-blackout" />
            <span>Investigation alert</span>
          </div>
          <div className="legend-item">
            <span className="legend-symbol legend-zone" />
            <span>Coastal zone envelope</span>
          </div>
          <div className="legend-item">
            <span className="legend-symbol legend-scenario" />
            <span>Illustrative case study</span>
          </div>
        </div>
        <div className="legend-note">
          Zone rectangles are provisional catalog search envelopes, not legal
          boundaries. Case-study layers are illustrative synthetic records generated
          for platform evaluation.
        </div>
      </div>
    </div>
  );
}
