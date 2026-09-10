import React from "react";
import { Marker, Popup, Polyline } from "react-leaflet";
import L from "leaflet";

const cutterIcon = L.divIcon({
  className: "custom-icg-icon",
  html: `<div style="
    background-color: #0077b6;
    color: #ffffff;
    width: 24px;
    height: 24px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    border: 2px solid #90e0ef;
    box-shadow: 0 0 10px rgba(0,180,216,0.8);
  ">🚢</div>`,
  iconSize: [24, 24],
  iconAnchor: [12, 12],
});

const mrccIcon = L.divIcon({
  className: "custom-mrcc-icon",
  html: `<div style="
    background-color: #1b263b;
    color: #ffd166;
    width: 26px;
    height: 26px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    border: 2px solid #ffd166;
    box-shadow: 0 0 10px rgba(255,209,102,0.6);
  ">⚓</div>`,
  iconSize: [26, 26],
  iconAnchor: [13, 13],
});

export default function ICGCuttersLayer({ caseId = 1 }) {
  // Assets for Case 1 (Kochi) and Case 2 (Mumbai)
  const isKochi = caseId === 1;

  const cutters = isKochi
    ? [
        {
          name: "ICGS Samrat (PRV 45)",
          type: "Pollution Response Vessel (Tier-1 NOS-DCP)",
          lat: 9.88,
          lon: 76.12,
          speed: "14 knots",
          equipment: "Ro-Boom 2000m + Dynamic Disc Skimmer 100 TPH",
          status: "ON ACTIVE INTERCEPT PATROL",
        },
        {
          name: "ICGS Sankalp (AOPV 46)",
          type: "Advanced Offshore Patrol Vessel",
          lat: 9.35,
          lon: 75.82,
          speed: "18 knots",
          equipment: "Helo Deck + High-Pressure Dispersant Sprayers",
          status: "DEPLOYED TO CORDON HIGHWAY",
        },
      ]
    : [
        {
          name: "ICGS Samudra Prahari (PCV 01)",
          type: "Specialised Marine Pollution Control Vessel",
          lat: 18.75,
          lon: 72.65,
          speed: "15 knots",
          equipment: "Ocean Boom 3000m + Oil Mop Skimmer",
          status: "CORDONING JNPT FAIRWAY",
        },
      ];

  const mrccStation = isKochi
    ? {
        name: "MRCC Kochi (Indian Coast Guard)",
        lat: 9.965,
        lon: 76.242,
        command: "Coast Guard District Headquarters No. 4 (Kerala & Mahe)",
      }
    : {
        name: "MRCC Mumbai (Indian Coast Guard)",
        lat: 18.928,
        lon: 72.835,
        command: "Coast Guard Regional Headquarters (West)",
      };

  // Approximate 12 nautical mile territorial sea limit
  const territorialBoundary = isKochi
    ? [
        [10.25, 75.95],
        [9.85, 76.05],
        [9.45, 76.15],
        [9.15, 76.25],
      ]
    : [
        [19.25, 72.55],
        [18.85, 72.58],
        [18.45, 72.62],
      ];

  return (
    <>
      {/* 12 NM Territorial Sea Limit */}
      <Polyline
        positions={territorialBoundary}
        pathOptions={{
          color: "#48cae4",
          weight: 2,
          dashArray: "8, 10",
          opacity: 0.6,
        }}
      >
        <Popup>
          <strong>12 NM Territorial Sea Limit (Indian Sovereign Jurisdiction)</strong>
          <p>Direct statutory enforcement under Merchant Shipping Act 1958 §356.</p>
        </Popup>
      </Polyline>

      {/* MRCC Base Marker */}
      <Marker position={[mrccStation.lat, mrccStation.lon]} icon={mrccIcon}>
        <Popup>
          <div className="popup-content">
            <h4 style={{ color: "#ffd166" }}>{mrccStation.name}</h4>
            <p><strong>{mrccStation.command}</strong></p>
            <p>Directs offshore Dornier sorties and statutory port detention orders.</p>
          </div>
        </Popup>
      </Marker>

      {/* Coast Guard Cutters */}
      {cutters.map((c) => (
        <Marker key={c.name} position={[c.lat, c.lon]} icon={cutterIcon}>
          <Popup>
            <div className="popup-content">
              <h4 style={{ color: "#00b4d8" }}>{c.name}</h4>
              <p>Type: <strong>{c.type}</strong></p>
              <p>Speed: <strong>{c.speed}</strong></p>
              <p>Equipment: {c.equipment}</p>
              <div style={{ marginTop: "6px" }}>
                <span className="badge badge-info">{c.status}</span>
              </div>
            </div>
          </Popup>
        </Marker>
      ))}
    </>
  );
}
