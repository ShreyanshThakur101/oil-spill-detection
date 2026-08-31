import React from "react";

export default function CaseSelector({ cases, selectedCaseId, onSelectCase, onRunPipeline, loading }) {
  return (
    <div className="card case-selector-card">
      <div className="card-header">
        <h2>Target Incident</h2>
        <span className="badge badge-primary">Demo Active</span>
      </div>
      <div className="form-group">
        <label htmlFor="case-select">Select Incident Case:</label>
        <select
          id="case-select"
          value={selectedCaseId || ""}
          onChange={(e) => onSelectCase(Number(e.target.value))}
          disabled={loading}
        >
          {cases.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
      </div>

      <button
        className="btn btn-primary btn-run"
        onClick={onRunPipeline}
        disabled={loading || !selectedCaseId}
      >
        {loading ? "Running Pipeline..." : "⚡ Run Detection & Attribution"}
      </button>
    </div>
  );
}
