import React from "react";
import { GeoJSON } from "react-leaflet";

export default function DriftLayer({ geojson }) {
  if (!geojson) return null;

  const style = {
    color: "#0077b6",
    weight: 2,
    dashArray: "4, 6",
    fillColor: "#48cae4",
    fillOpacity: 0.35
  };

  return <GeoJSON key={JSON.stringify(geojson)} data={geojson} style={style} />;
}
