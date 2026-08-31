import React from "react";
import { GeoJSON } from "react-leaflet";

export default function AISTrackLayer({ vessels, selectedMmsi, onSelectVessel }) {
  if (!vessels || vessels.length === 0) return null;

  return (
    <>
      {vessels.map((v) => {
        if (!v.track_geojson) return null;
        const isSelected = v.mmsi === selectedMmsi;
        const style = {
          color: isSelected ? "#ffd166" : "#06d6a0",
          weight: isSelected ? 5 : 2.5,
          opacity: isSelected ? 1.0 : 0.75,
          dashArray: isSelected ? null : "3, 3"
        };

        return (
          <GeoJSON
            key={`${v.mmsi}-${isSelected}`}
            data={v.track_geojson}
            style={style}
            eventHandlers={{
              click: () => onSelectVessel && onSelectVessel(v.mmsi)
            }}
          />
        );
      })}
    </>
  );
}
