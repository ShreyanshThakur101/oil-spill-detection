import React from "react";

export default function ConfidencePanel({ detection, drift }) {
  if (!detection && !drift) return null;

  return (
    <div className="card confidence-panel">
      <div className="metrics-grid">
        {detection && (
          <div className="metric-box">
            <span className="metric-label">SAR Detection Confidence</span>
            <span className="metric-value">{Math.round(detection.confidence * 100)}%</span>
            <span className="metric-sub">
              Area: {detection.shape_features?.area_km2} km² | Age: {detection.shape_features?.age_class}
            </span>
          </div>
        )}

        {drift && (
          <div className="metric-box">
            <span className="metric-label">Drift Origin Uncertainty</span>
            <span className="metric-value">±{drift.uncertainty_radius_km} km</span>
            <span className="metric-sub">
              Est. Time: {new Date(drift.estimated_origin_time).toUTCString()}
            </span>
          </div>
        )}
      </div>

      <div className="disclaimer-alert">
        <strong>⚖️ Decision-Support Notice:</strong> Attribution scores represent probabilistic spatial-temporal correlation and environmental drift likelihood. Output is designed for investigative prioritization, not legal proof.
      </div>
    </div>
  );
}
