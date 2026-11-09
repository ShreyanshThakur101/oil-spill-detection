import React from "react";
import { useDemo } from "../context/DemoContext";

/**
 * ScenarioSelector — dropdown + reset control for the five nationwide
 * case studies. The underlying records retain explicit synthetic provenance.
 */
export default function ScenarioSelector() {
  const { scenarios, selectedScenario, selectScenario, reset, loading } = useDemo();

  return (
    <div className="scenario-selector">
      <span className="scenario-selector-label">🛰 CASE STUDY</span>
      <select
        className="scenario-select"
        aria-label="Select case study"
        value={selectedScenario || ""}
        onChange={(e) => selectScenario(e.target.value)}
        disabled={loading || scenarios.length === 0}
      >
        {scenarios.length === 0 && <option value="">Loading case studies…</option>}
        {scenarios.map((s) => (
          <option key={s.id} value={s.id}>
            {s.name}
          </option>
        ))}
      </select>

      <button
        type="button"
        className="btn-reset-cases"
        onClick={reset}
        disabled={loading}
        title="Reload the five case-study records (repeatable)"
      >
        {loading ? "Refreshing…" : "↺ Reset Case Records"}
      </button>
    </div>
  );
}
