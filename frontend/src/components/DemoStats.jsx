import React from "react";
import { useDemo } from "../context/DemoContext";

/**
 * DemoStats — a compact panel showing aggregate stats for the active case
 * study. Updates automatically when the case study changes.
 */
export default function DemoStats() {
  const { scenarioData, selectedScenario, scenarios } = useDemo();

  if (!scenarioData) {
    return (
      <div style={{ padding: "12px 14px", color: "#64748b", fontSize: "12px" }}>
        No case study loaded.
      </div>
    );
  }

  const scenarioName =
    scenarios.find((s) => s.id === selectedScenario)?.name || selectedScenario;

  const { detections = [], vessels = [], incidents = [], scenes = [] } = scenarioData;

  const stat = (label, value, color = "#38bdf8") => (
    <div
      key={label}
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        padding: "8px 12px",
        background: "#0f172a",
        borderRadius: "6px",
        minWidth: "90px",
      }}
    >
      <span style={{ fontSize: "22px", fontWeight: 700, color }}>{value}</span>
      <span style={{ fontSize: "10px", color: "#94a3b8", marginTop: "2px", textAlign: "center" }}>
        {label}
      </span>
    </div>
  );

  return (
    <div
      style={{
        background: "#1e293b",
        border: "1px solid #334155",
        borderRadius: "8px",
        padding: "12px 14px",
        margin: "10px 0",
      }}
    >
      <div
        style={{
          color: "#94a3b8",
          fontSize: "11px",
          fontWeight: 700,
          letterSpacing: "0.08em",
          marginBottom: "10px",
          textTransform: "uppercase",
        }}
      >
        📊 Case Study Record — {scenarioName}
      </div>

      <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
        {stat("Observations", scenes.length, "#a78bfa")}
        {stat("Slick detections", detections.length, "#f87171")}
        {stat("Vessel candidates", vessels.length, "#38bdf8")}
        {stat("Investigations", incidents.length, "#fb923c")}
      </div>

      <div
        style={{
          marginTop: "10px",
          fontSize: "10px",
          color: "#475569",
          fontStyle: "italic",
        }}
      >
        Illustrative synthetic case-study records — not verified observations.
      </div>
    </div>
  );
}
