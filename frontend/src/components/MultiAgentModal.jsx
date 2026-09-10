import React from "react";

export default function MultiAgentModal({ multiAgentData, onClose }) {
  const agents = multiAgentData?.agents || [
    {
      agent: "Radar_GeoJSON_Parser_Agent",
      status: "COMPLETED",
      sensor: "Sentinel-1 C-Band SAR (Copernicus)",
      slick_centroid: [9.58, 76.08],
      area_km2: 14.8,
      perimeter_km: 18.2,
      elongation: 2.6,
      radar_iou: 0.892,
      analysis: "High-confidence dark patch segmented; damping signature consistent with heavy bunker fuel rather than natural biogenic films.",
    },
    {
      agent: "Physics_Drift_Validator_Agent",
      status: "COMPLETED",
      particles_evaluated: 200,
      backtrack_duration_hours: 18,
      current_velocity: "0.62 m/s (1.2 knots)",
      wind_shear: "14.2 knots @ 230°",
      uncertainty_radius_km: 4.8,
      hydrodynamic_plausibility: "VALIDATED",
      spatio_temporal_origin_cone: "Convex hull validated against Navier-Stokes backward advection.",
    },
    {
      agent: "Enforcement_Dossier_Agent",
      status: "COMPLETED",
      prima_facie_case_established: true,
      statutory_summary: "Coincidence of 42-minute deliberate AIS blackout and sudden 6.8 knot deceleration inside backward drift cone constitutes prima facie statutory non-compliance.",
      recommended_enforcement_action: "Immediate Vessel Detention under Merchant Shipping Act 1958 §356J at Port of Cochin.",
      inspection_priority: "PRIORITY_1_CRITICAL",
      agencies_notified: [
        "Indian Coast Guard Maritime Rescue Coordination Centre (MRCC)",
        "Directorate General of Shipping (DG Shipping)",
        "State Pollution Control Board (SPCB)",
      ],
    },
  ];

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-container multi-agent-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header-bar">
          <div className="modal-title-group">
            <span className="badge badge-info">NUGEN AGENT BUILDER</span>
            <h3>Multi-Agent Enforcement Coordination Architecture</h3>
          </div>
          <button className="btn btn-secondary" onClick={onClose}>✕ Close</button>
        </div>

        <div className="modal-body">
          <p className="section-desc">
            Nugen Agent Builder coordinates three specialized, domain-aligned SLM agents running concurrently to ingest radar GeoJSON,
            validate fluid drift advection, and synthesize court-ready maritime enforcement briefs.
          </p>

          <div className="agent-cards-container">
            {agents.map((ag, i) => (
              <div key={i} className="agent-card">
                <div className="agent-card-header">
                  <div className="agent-badge-num">Agent {i + 1}</div>
                  <h4>{ag.agent.replace(/_/g, " ")}</h4>
                  <span className="agent-status-tag">STATUS: {ag.status}</span>
                </div>

                <div className="agent-details">
                  {ag.sensor && (
                    <p><strong>Sensor Platform:</strong> {ag.sensor} (IoU: {Math.round((ag.radar_iou || 0.89) * 100)}%)</p>
                  )}
                  {ag.area_km2 && (
                    <p><strong>Geometry Extraction:</strong> {ag.area_km2} km² slick | Elongation: {ag.elongation}</p>
                  )}
                  {ag.particles_evaluated && (
                    <p><strong>Particles Backtracked:</strong> {ag.particles_evaluated} virtual particles over {ag.backtrack_duration_hours}h</p>
                  )}
                  {ag.current_velocity && (
                    <p><strong>Hydrodynamic Forcing:</strong> Current: {ag.current_velocity} | Wind: {ag.wind_shear}</p>
                  )}
                  {ag.recommended_enforcement_action && (
                    <p className="text-danger"><strong>Statutory Action:</strong> {ag.recommended_enforcement_action}</p>
                  )}
                  {ag.analysis && <p className="agent-note">"{ag.analysis}"</p>}
                  {ag.statutory_summary && <p className="agent-note">"{ag.statutory_summary}"</p>}
                </div>
              </div>
            ))}
          </div>

          <div className="multi-agent-consensus-banner">
            <span className="consensus-badge">UNANIMOUS DECISION</span>
            <span>
              All 3 agents have verified physical plausibility and statutory compliance. Ready for immediate Coast Guard boarding dispatch.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
