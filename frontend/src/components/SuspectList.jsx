import React from "react";

export default function SuspectList({ vessels, selectedMmsi, onSelectVessel }) {
  if (!vessels || vessels.length === 0) {
    return (
      <div className="card suspect-panel">
        <h3>Ranked Suspect Vessels</h3>
        <p className="placeholder-text">Run pipeline to compute attribution scores.</p>
      </div>
    );
  }

  return (
    <div className="card suspect-panel">
      <div className="card-header">
        <h3>Ranked Suspect Vessels</h3>
        <span className="badge badge-info">{vessels.length} Evaluated</span>
      </div>

      <div className="vessel-list">
        {vessels.map((vessel, idx) => {
          const isSelected = vessel.mmsi === selectedMmsi;
          const scorePercent = Math.round(vessel.final_score * 100);

          return (
            <div
              key={vessel.mmsi}
              className={`vessel-card ${isSelected ? "selected" : ""}`}
              onClick={() => onSelectVessel(vessel.mmsi)}
            >
              <div className="vessel-card-header">
                <span className="vessel-rank">#{idx + 1}</span>
                <span className="vessel-name">{vessel.vessel_name}</span>
                <span className="vessel-type-badge">{vessel.vessel_type}</span>
              </div>

              <div className="score-row">
                <span>Attribution Likelihood:</span>
                <span className="score-value">{scorePercent}%</span>
              </div>

              <div className="score-bar-bg">
                <div
                  className={`score-bar-fill ${scorePercent > 70 ? "high" : scorePercent > 40 ? "medium" : "low"}`}
                  style={{ width: `${scorePercent}%` }}
                ></div>
              </div>

              <p className="explanation-text">{vessel.explanation}</p>

              {vessel.scores && (
                <div className="sub-scores-grid">
                  <div className="sub-score-item">
                    <span className="sub-score-label">Proximity</span>
                    <span className="sub-score-val">{Math.round((vessel.scores.proximity || 0) * 100)}%</span>
                  </div>
                  <div className="sub-score-item">
                    <span className="sub-score-label">Temporality</span>
                    <span className="sub-score-val">{Math.round((vessel.scores.temporality || 0) * 100)}%</span>
                  </div>
                  <div className="sub-score-item">
                    <span className="sub-score-label">AIS Gap</span>
                    <span className="sub-score-val">{Math.round((vessel.scores.ais_gap || 0) * 100)}%</span>
                  </div>
                  <div className="sub-score-item">
                    <span className="sub-score-label">Type Prior</span>
                    <span className="sub-score-val">{Math.round((vessel.scores.vessel_type_prior || 0) * 100)}%</span>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
