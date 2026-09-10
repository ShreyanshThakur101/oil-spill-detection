import React from "react";
import { GeoJSON } from "react-leaflet";
import L from "leaflet";

export default function DriftLayer({ originGeojson, particlesGeojson, trajectoriesGeojson }) {
  const originStyle = {
    color: "#00b4d8",
    weight: 2.5,
    dashArray: "6, 6",
    fillColor: "#0077b6",
    fillOpacity: 0.28,
  };

  const trajectoryStyle = {
    color: "#48cae4",
    weight: 1.2,
    opacity: 0.45,
    dashArray: "2, 4",
  };

  const pointToLayer = (feature, latlng) => {
    return L.circleMarker(latlng, {
      radius: 2.5,
      fillColor: "#90e0ef",
      color: "#0077b6",
      weight: 1,
      opacity: 0.9,
      fillOpacity: 0.85,
    });
  };

  return (
    <>
      {trajectoriesGeojson && (
        <GeoJSON
          key={`traj-${JSON.stringify(trajectoriesGeojson).length}`}
          data={trajectoriesGeojson}
          style={trajectoryStyle}
        />
      )}
      {originGeojson && (
        <GeoJSON
          key={`origin-${JSON.stringify(originGeojson).length}`}
          data={originGeojson}
          style={originStyle}
        />
      )}
      {particlesGeojson && (
        <GeoJSON
          key={`particles-${JSON.stringify(particlesGeojson).length}`}
          data={particlesGeojson}
          pointToLayer={pointToLayer}
        />
      )}
    </>
  );
}
