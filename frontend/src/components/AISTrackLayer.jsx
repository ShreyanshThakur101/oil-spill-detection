import React from "react";
import { GeoJSON, Marker, Popup, Polyline } from "react-leaflet";
import L from "leaflet";

// Create custom vessel marker icon
const createVesselIcon = (color, isSuspect = false) =>
  L.divIcon({
    className: "custom-vessel-icon",
    html: `<div style="
      background-color: ${color};
      width: ${isSuspect ? "14px" : "10px"};
      height: ${isSuspect ? "14px" : "10px"};
      border-radius: 50%;
      border: 2px solid #ffffff;
      box-shadow: 0 0 ${isSuspect ? "8px #ff4757" : "4px rgba(0,0,0,0.5)"};
    "></div>`,
    iconSize: [14, 14],
    iconAnchor: [7, 7],
  });

export default function AISTrackLayer({ vessels, selectedMmsi, onSelectVessel }) {
  if (!vessels || vessels.length === 0) return null;

  return (
    <>
      {vessels.map((v) => {
        if (!v.track_geojson) return null;
        const isSelected = v.mmsi === selectedMmsi;
        const isCritical = v.final_score >= 0.85;

        const style = {
          color: isSelected ? "#ffba08" : isCritical ? "#ff4757" : "#06d6a0",
          weight: isSelected ? 4.5 : isCritical ? 3.5 : 2.0,
          opacity: isSelected ? 1.0 : isCritical ? 0.95 : 0.75,
          dashArray: isSelected ? null : "4, 4",
        };

        const coords = v.track_geojson.coordinates || [];
        const lastCoord = coords.length > 0 ? coords[coords.length - 1] : null;
        const lastLatLng = lastCoord ? [lastCoord[1], lastCoord[0]] : null;

        return (
          <React.Fragment key={v.mmsi}>
            <GeoJSON
              key={`track-${v.mmsi}-${isSelected}`}
              data={v.track_geojson}
              style={style}
              eventHandlers={{
                click: () => onSelectVessel && onSelectVessel(v.mmsi),
              }}
            />

            {/* Deliberate AIS Blackout Gap Zone (Red Dashed Segment) */}
            {v.gap_coordinates && v.gap_coordinates.length >= 2 && (
              <Polyline
                positions={v.gap_coordinates.map((c) => [c[1], c[0]])}
                pathOptions={{
                  color: "#ff0055",
                  weight: 5,
                  dashArray: "6, 8",
                  opacity: 0.95,
                }}
              >
                <Popup>
                  <div className="popup-content">
                    <strong style={{ color: "#ff0055" }}>⚠️ DELIBERATE AIS BLACKOUT ZONE</strong>
                    <p style={{ margin: "4px 0" }}>
                      Vessel: <strong>{v.vessel_name}</strong> (MMSI {v.mmsi})
                    </p>
                    <p style={{ margin: "4px 0" }}>
                      Duration: <strong>{v.ais_gap_duration_mins} Minutes</strong>
                    </p>
                    <small>Transponder switched off inside backward drift release cone.</small>
                  </div>
                </Popup>
              </Polyline>
            )}

            {lastLatLng && (
              <Marker
                position={lastLatLng}
                icon={createVesselIcon(
                  isSelected ? "#ffba08" : isCritical ? "#ff4757" : "#06d6a0",
                  isCritical
                )}
                eventHandlers={{
                  click: () => onSelectVessel && onSelectVessel(v.mmsi),
                }}
              >
                <Popup>
                  <div className="popup-content">
                    <h4>{v.vessel_name}</h4>
                    <p>MMSI: <strong>{v.mmsi}</strong> | Flag: <strong>{v.flag_name}</strong></p>
                    <p>Type: <strong>{v.vessel_type}</strong> | Draft: {v.draft_m}m</p>
                    <p>Attribution Likelihood: <strong>{Math.round(v.final_score * 100)}%</strong></p>
                    {v.speed_drop_knots > 0 && (
                      <p>Speed Deceleration: <strong style={{ color: "#ff4757" }}>-{v.speed_drop_knots} kt</strong></p>
                    )}
                    {v.ais_gap_duration_mins > 0 && (
                      <p>AIS Blackout: <strong style={{ color: "#ff4757" }}>{v.ais_gap_duration_mins} min</strong></p>
                    )}
                    <div style={{ marginTop: "6px" }}>
                      <span className={`badge ${isCritical ? "badge-danger" : "badge-info"}`}>
                        {v.status_code || "EVALUATED"}
                      </span>
                    </div>
                  </div>
                </Popup>
              </Marker>
            )}
          </React.Fragment>
        );
      })}
    </>
  );
}
