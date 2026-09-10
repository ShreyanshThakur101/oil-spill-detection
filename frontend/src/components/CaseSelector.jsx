import React from "react";

export default function CaseSelector({
  cases,
  selectedCaseId,
  onSelectCase,
  onRunPipeline,
  loading,
}) {
  const selectedCase = cases.find((c) => c.id === selectedCaseId);

  return (
    <div className="card case-selector-card">
      <div className="card-header">
        <div>
          <h2>Target Spill Incident</h2>
          <span className="case-sub">Verified Historical Benchmark</span>
        </div>
        <span className="badge badge-success">PHASE 1 MVP</span>
      </div>

      <div className="form-group">
        <label htmlFor="case-select">Select EEZ Incident Corridor:</label>
        <select
          id="case-select"
          value={selectedCaseId || ""}
          onChange={(e) => onSelectCase(Number(e.target.value))}
          disabled={loading}
          className="form-control"
        >
          {cases.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
      </div>

      {selectedCase && (
        <div className="case-meta-preview">
          <p className="case-desc">{selectedCase.description}</p>
        </div>
      )}

      <button
        className={`btn btn-primary btn-run ${loading ? "btn-running" : ""}`}
        onClick={onRunPipeline}
        disabled={loading || !selectedCaseId}
      >
        {loading ? (
          <span className="running-spinner">⚡ Running 5-Stage Physics+AI Pipeline...</span>
        ) : (
          "⚡ Run Detection & Attribution Pipeline"
        )}
      </button>

      {loading && (
        <div className="pipeline-steps-ticker">
          <div className="ticker-step active">1. Ingesting Sentinel-1 C-Band SAR GRD...</div>
          <div className="ticker-step active">2. OpenDrift 200-Particle Backward Advection (18h)...</div>
          <div className="ticker-step active">3. Screening GFW AIS Corridor Candidates (34 vessels)...</div>
          <div className="ticker-step active">4. 6-Factor Anomaly & Blackout Correlation...</div>
          <div className="ticker-step active">5. Nugen SLM Citing Merchant Shipping Act §356...</div>
        </div>
      )}
    </div>
  );
}
