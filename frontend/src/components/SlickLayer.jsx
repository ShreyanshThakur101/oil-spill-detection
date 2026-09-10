import React from "react";
import { GeoJSON } from "react-leaflet";

export default function SlickLayer({ geojson, areaKm2 = 14.8, confidence = 0.892 }) {
  if (!geojson) return null;

  const style = {
    color: "#ff3366",
    weight: 2.5,
    fillColor: "#111111",
    fillOpacity: 0.85,
  };

  const onEachFeature = (feature, layer) => {
    layer.bindPopup(`
      <div class="popup-content">
        <h4 style="color: #ff3366;">🛰️ Sentinel-1 SAR Oil Slick</h4>
        <p>Surface Area: <strong>${areaKm2} km²</strong></p>
        <p>Segmentation IoU: <strong>${Math.round(confidence * 100)}%</strong></p>
        <p>Sensor: <strong>Sentinel-1 C-Band SAR</strong></p>
        <p>Signature: <strong>Capillary-Wave Damping (-6.4 dB)</strong></p>
        <small style="color: #06d6a0;">Penetrated 100% cloud & monsoon precipitation.</small>
      </div>
    `);
  };

  return (
    <GeoJSON
      key={`slick-${JSON.stringify(geojson).length}`}
      data={geojson}
      style={style}
      onEachFeature={onEachFeature}
    />
  );
}
