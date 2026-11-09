import React from "react";
import { GeoJSON, CircleMarker, Polyline, Tooltip, Popup } from "react-leaflet";
import { useDemo } from "../context/DemoContext";

/**
 * DemoLayers — renders the active illustrative case-study data on a Leaflet
 * map:
 *   • Detection polygons (red fill)
 *   • Backward-drift origin cones (orange dashed)
 *   • Drift trajectories (orange dashed polylines)
 *   • Ranked vessel positions (blue markers)
 *   • Investigation alert rings (red dashed)
 *
 * Must be rendered inside a <MapContainer>.
 */
export default function DemoLayers({ showIncidents = true }) {
  const { scenarioData } = useDemo();
  if (!scenarioData) return null;

  const { detections = [], vessels = [], drift = [], incidents = [] } = scenarioData;

  const vesselById = Object.fromEntries(
    vessels.map((v) => [v.vessel_id, v])
  );

  const detectionStyle = {
    color: "#ef4444",
    fillColor: "#ef4444",
    fillOpacity: 0.32,
    weight: 2,
  };

  const originStyle = {
    color: "#fb923c",
    fillColor: "#fb923c",
    fillOpacity: 0.12,
    weight: 2,
    dashArray: "7 5",
  };

  return (
    <>
      {/* Detection polygons */}
      {detections.map((det) => {
        const geo = det.polygon || det.polygon_geojson;
        if (!geo) return null;
        return (
          <GeoJSON
            key={`det-${det.id}`}
            data={geo}
            style={detectionStyle}
            onEachFeature={(_feature, layer) => {
              layer.bindTooltip(
                `Illustrative detection · ${det.sector || "Unassigned sector"}<br/>` +
                  `Confidence: ${det.confidence ?? "N/A"}<br/>` +
                  `Area: ${det.area_sqkm ?? "N/A"} km²`,
                { sticky: true }
              );
            }}
          />
        );
      })}

      {/* Backward drift origin cones */}
      {drift.map((dr) => {
        if (!dr.origin_polygon) return null;
        return (
          <GeoJSON
            key={`origin-${dr.detection_id}`}
            data={dr.origin_polygon}
            style={originStyle}
            onEachFeature={(_feature, layer) => {
              layer.bindTooltip(
                `Illustrative drift origin<br/>` +
                  `Uncertainty: ${dr.uncertainty_km ?? "N/A"} km<br/>` +
                  `Particles: ${dr.particle_count ?? 200}`,
                { sticky: true }
              );
            }}
          />
        );
      })}

      {/* Drift trajectories */}
      {drift.map((dr) => {
        const traj = dr.trajectories || [];
        if (traj.length < 2) return null;
        const positions = traj.map((t) => [t.position.lat, t.position.lon]);
        return (
          <Polyline
            key={`drift-${dr.detection_id}`}
            positions={positions}
            pathOptions={{ color: "#fb923c", weight: 2, dashArray: "6 4" }}
          >
            <Tooltip>
              Illustrative drift estimate · uncertainty {dr.uncertainty_km} km
            </Tooltip>
          </Polyline>
        );
      })}

      {/* Incident alert rings */}
      {showIncidents &&
        incidents.map((incident) => {
          const vessel = vesselById[incident.vessel_id];
          if (!vessel?.position) return null;
          const color =
            incident.severity === "CRITICAL"
              ? "#ff3366"
              : incident.severity === "HIGH"
              ? "#fb7185"
              : "#fbbf24";
          return (
            <CircleMarker
              key={`inc-${incident.incident_id}`}
              center={[vessel.position.lat, vessel.position.lon]}
              radius={16}
              pathOptions={{
                color,
                weight: 2,
                fillOpacity: 0,
                dashArray: "4 3",
              }}
            >
              <Tooltip>
                {incident.incident_id} — {incident.severity} / {incident.status}
                <br />
                {incident.title}
              </Tooltip>
            </CircleMarker>
          );
        })}

      {/* Ranked vessels */}
      {vessels.map((vessel) => {
        const pos = vessel.position;
        if (!pos?.lat || !pos?.lon) return null;
        const score = vessel.attribution_score ?? 0;
        const color = score >= 0.8 ? "#38bdf8" : score >= 0.5 ? "#facc15" : "#94a3b8";
        return (
          <CircleMarker
            key={`vsl-${vessel.vessel_id}`}
            center={[pos.lat, pos.lon]}
            radius={score >= 0.8 ? 10 : 7}
            pathOptions={{
              color,
              fillColor: color,
              fillOpacity: 0.85,
              weight: 2,
            }}
          >
            <Popup>
              <div style={{ minWidth: 210, fontSize: 12 }}>
                <strong>{vessel.name}</strong>
                <div>Rank #{vessel.rank} • score {Math.round(score * 100)}%</div>
                <div>MMSI {vessel.mmsi} • {vessel.flag_name || vessel.flag}</div>
                <div>{vessel.type}</div>
                <div>AIS gap: {vessel.ais_gap_minutes} min</div>
                <div>Speed drop: {vessel.speed_drop_knots} kt</div>
                <div>Destination: {vessel.destination}</div>
                <div style={{ marginTop: 6, color: "#92400e", fontWeight: 700 }}>
                  Illustrative record · synthetic AIS track
                </div>
              </div>
            </Popup>
          </CircleMarker>
        );
      })}
    </>
  );
}
