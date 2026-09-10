import React from "react";

export default function SuspectList({
  vessels,
  selectedMmsi,
  onSelectVessel,
  onOpenDossier,
}) {
  if (!vessels || vessels.length === 0) {
    return (
      <div className="card suspect-panel">
        <div className="card-header">
          <h3>Ranked Suspect Evidence Scoreboard</h3>
          <span className="badge badge-secondary">Awaiting Pipeline</span>
        </div>
        <p className="placeholder-text">
          Run the end-to-end attribution pipeline to screen transiting corridor traffic against the backward drift cone.
        </p>
      </div>
    );
  }

  return (
    <div className="card suspect-panel">
      <div className="card-header">
        <div>
          <h3>Ranked Evidence Scoreboard (6-Factor)</h3>
          <p className="card-subtitle">34 transiting candidates screened • 32 ruled out via hydrodynamic drift</p>
        </div>
        <span className="badge badge-info">{vessels.length} Correlated</span>
      </div>

      <div className="vessel-list">
        {vessels.map((vessel, idx) => {
          const isSelected = vessel.mmsi === selectedMmsi;
          const scorePercent = Math.round(vessel.final_score * 100);
          const isCritical = vessel.final_score >= 0.85;

          return (
            <div
              key={vessel.mmsi}
              className={`vessel-card ${isSelected ? "selected" : ""} ${isCritical ? "critical-card" : ""}`}
              onClick={() => onSelectVessel(vessel.mmsi)}
            >
              <div className="vessel-card-header">
                <div className="vessel-title-group">
                  <span className="vessel-rank">#{idx + 1}</span>
                  <span className="vessel-name">{vessel.vessel_name}</span>
                  <span className="flag-tag">{vessel.flag_name} ({vessel.flag})</span>
                </div>
                <span className={`status-pill ${isCritical ? "status-danger" : "status-neutral"}`}>
                  {isCritical ? "PRIMA FACIE SUSPECT" : "ROUTINE TRANSIT"}
                </span>
              </div>

              <div className="telemetry-row">
                <div className="telemetry-item">
                  <span className="telemetry-label">MMSI:</span>
                  <span className="telemetry-val">{vessel.mmsi}</span>
                </div>
                <div className="telemetry-item">
                  <span className="telemetry-label">Class:</span>
                  <span className="telemetry-val">{vessel.vessel_type}</span>
                </div>
                <div className="telemetry-item">
                  <span className="telemetry-label">AIS Blackout:</span>
                  <span className={`telemetry-val ${vessel.ais_gap_duration_mins >= 30 ? "text-danger" : ""}`}>
                    {vessel.ais_gap_duration_mins > 0 ? `${vessel.ais_gap_duration_mins} mins` : "None"}
                  </span>
                </div>
                <div className="telemetry-item">
                  <span className="telemetry-label">Speed Decel:</span>
                  <span className={`telemetry-val ${vessel.speed_drop_knots >= 4 ? "text-danger" : ""}`}>
                    {vessel.speed_drop_knots > 0 ? `-${vessel.speed_drop_knots} kt` : "0.0 kt"}
                  </span>
                </div>
              </div>

              <div className="score-row">
                <span className="score-label">Composite Attribution Likelihood:</span>
                <span className={`score-value ${scorePercent > 80 ? "high" : scorePercent > 40 ? "medium" : "low"}`}>
                  {scorePercent}%
                </span>
              </div>

              <div className="score-bar-bg">
                <div
                  className={`score-bar-fill ${scorePercent > 80 ? "high" : scorePercent > 40 ? "medium" : "low"}`}
                  style={{ width: `${scorePercent}%` }}
                ></div>
              </div>

              <p className="explanation-text">
                <strong>Attribution Finding:</strong> {vessel.explanation}
              </p>

              {/* 6-Factor Breakdown Grid */}
              {vessel.scores && (
                <div className="sub-scores-grid">
                  <div className="sub-score-item">
                    <span className="sub-score-label">Proximity (Cone)</span>
                    <span className="sub-score-val">{Math.round((vessel.scores.proximity || 0) * 100)}%</span>
                  </div>
                  <div className="sub-score-item">
                    <span className="sub-score-label">Temporality</span>
                    <span className="sub-score-val">{Math.round((vessel.scores.temporality || 0) * 100)}%</span>
                  </div>
                  <div className="sub-score-item">
                    <span className="sub-score-label">AIS Blackout</span>
                    <span className="sub-score-val">{Math.round((vessel.scores.ais_gap || 0) * 100)}%</span>
                  </div>
                  <div className="sub-score-item">
                    <span className="sub-score-label">Speed Anomaly</span>
                    <span className="sub-score-val">{Math.round((vessel.scores.speed_anomaly || 0) * 100)}%</span>
                  </div>
                  <div className="sub-score-item">
                    <span className="sub-score-label">Course Parity</span>
                    <span className="sub-score-val">{Math.round((vessel.scores.parity || 0) * 100)}%</span>
                  </div>
                  <div className="sub-score-item">
                    <span className="sub-score-label">Vessel Prior</span>
                    <span className="sub-score-val">{Math.round((vessel.scores.vessel_type_prior || 0) * 100)}%</span>
                  </div>
                </div>
              )}

              {/* Action Button */}
              <div className="card-actions">
                <button
                  className="btn btn-sm btn-outline-dossier"
                  onClick={(e) => {
                    e.stopPropagation();
                    onOpenDossier && onOpenDossier(vessel);
                  }}
                >
                  📜 View Court-Ready ICG Dossier
                </button>
                {isCritical && (
                  <span className="detention-tag">⚠️ Statutory Detention Recommended (§356J)</span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
