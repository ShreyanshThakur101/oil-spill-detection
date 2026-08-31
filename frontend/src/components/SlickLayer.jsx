import React from "react";
import { GeoJSON } from "react-leaflet";

export default function SlickLayer({ geojson }) {
  if (!geojson) return null;

  const style = {
    color: "#e63946",
    weight: 3,
    fillColor: "#d90429",
    fillOpacity: 0.65
  };

  return <GeoJSON key={JSON.stringify(geojson)} data={geojson} style={style} />;
}
