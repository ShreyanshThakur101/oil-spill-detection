import React from "react";

export default function LegalDossierModal({ dossier, onClose }) {
  if (!dossier) return null;

  const handlePrint = () => {
    window.print();
  };

  const s1 = dossier.section_1_satellite_radar || {};
  const s2 = dossier.section_2_drift_physics || {};
  const s3 = dossier.section_3_vessel_behavioral_telemetry || {};
  const s4 = dossier.section_4_statutory_citations || [];
  const s5 = dossier.section_5_enforcement_orders || {};
  const summary = dossier.case_summary || {};

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-container legal-dossier-modal" onClick={(e) => e.stopPropagation()}>
        {/* Modal Controls */}
        <div className="modal-header-bar no-print">
          <div className="modal-title-group">
            <span className="badge badge-warning">OFFICIAL ENFORCEMENT BRIEF</span>
            <h3>Maritime Pollution Legal Dossier (MARPOL / Merchant Shipping Act)</h3>
          </div>
          <div className="modal-actions">
            <button className="btn btn-primary" onClick={handlePrint}>
              🖨️ Print / Export to PDF
            </button>
            <button className="btn btn-secondary" onClick={onClose}>
              ✕ Close
            </button>
          </div>
        </div>

        {/* Printable Official Document Body */}
        <div className="dossier-document print-area">
          {/* Header Block */}
          <div className="dossier-header">
            <div className="emblem-box">
              <div className="icg-seal">⚓ BHARATIYA TATRAKSHAK ⚓</div>
              <div className="icg-sub">INDIAN COAST GUARD • MARITIME RESCUE COORDINATION CENTRE (MRCC)</div>
            </div>
            <div className="dossier-meta-table">
              <div><strong>DOSSIER REF:</strong> {dossier.dossier_id}</div>
              <div><strong>CLASSIFICATION:</strong> <span className="classification-tag">{dossier.classification}</span></div>
              <div><strong>DATE/TIME:</strong> {dossier.generated_timestamp}</div>
              <div><strong>JURISDICTION:</strong> {dossier.jurisdiction}</div>
            </div>
          </div>

          <div className="dossier-banner">
            <h2>STATUTORY INCIDENT REPORT & VESSEL DETENTION ORDER</h2>
            <p>Issued under Section 356J of the Indian Merchant Shipping Act, 1958 (Act 44 of 1958)</p>
          </div>

          {/* Incident Overview Card */}
          <div className="dossier-section summary-box">
            <div className="summary-grid">
              <div>
                <span className="lbl">Incident Name:</span>
                <span className="val">{summary.incident_name}</span>
              </div>
              <div>
                <span className="lbl">Target Vessel:</span>
                <span className="val highlight">{summary.target_vessel_name}</span>
              </div>
              <div>
                <span className="lbl">MMSI / IMO:</span>
                <span className="val">{summary.target_mmsi} / {summary.target_imo}</span>
              </div>
              <div>
                <span className="lbl">Flag State:</span>
                <span className="val">{summary.flag_state}</span>
              </div>
              <div>
                <span className="lbl">Attribution Confidence:</span>
                <span className="val confidence-high">{summary.composite_attribution_confidence}</span>
              </div>
              <div>
                <span className="lbl">Statutory Action:</span>
                <span className="val text-danger"><strong>{summary.enforcement_order}</strong></span>
              </div>
            </div>
          </div>

          {/* Section 1: Satellite Radar CV */}
          <div className="dossier-section">
            <h4 className="section-title">SECTION I: SATELLITE SYNTHETIC APERTURE RADAR (SAR) EVIDENCE</h4>
            <table className="dossier-table">
              <tbody>
                <tr>
                  <td><strong>Observation Platform</strong></td>
                  <td>{s1.satellite_platform}</td>
                  <td><strong>Detection Architecture</strong></td>
                  <td>{s1.detection_architecture}</td>
                </tr>
                <tr>
                  <td><strong>Slick Surface Area</strong></td>
                  <td><strong>{s1.slick_surface_area_km2} km²</strong></td>
                  <td><strong>Segmentation IoU Confidence</strong></td>
                  <td><strong>{s1.segmentation_iou_confidence}</strong> (Inference: {s1.inference_time_sec}s)</td>
                </tr>
                <tr>
                  <td><strong>Radar Damping Signature</strong></td>
                  <td colSpan="3">{s1.radar_damping_signature}</td>
                </tr>
                <tr>
                  <td><strong>Meteorological Reliability</strong></td>
                  <td colSpan="3">{s1.monsoon_penetration}</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Section 2: Hydrodynamic Backward Drift Physics */}
          <div className="dossier-section">
            <h4 className="section-title">SECTION II: HYDRODYNAMIC BACKWARD LAGRANGIAN RECONSTRUCTION (OPEN DRIFT)</h4>
            <p className="section-desc">
              Virtual water-surface particles (200 particles) back-propagated over 18 hours using Navier-Stokes fluid dynamics,
              forced with Copernicus Marine Service (CMEMS) currents and ECMWF ERA5 wind reanalysis.
            </p>
            <table className="dossier-table">
              <tbody>
                <tr>
                  <td><strong>Drift Simulation Model</strong></td>
                  <td>{s2.simulation_model} ({s2.particle_count} particles)</td>
                  <td><strong>Backtrack Duration</strong></td>
                  <td>{s2.backtrack_duration}</td>
                </tr>
                <tr>
                  <td><strong>Surface Current Vectors</strong></td>
                  <td>{s2.surface_current_vectors}</td>
                  <td><strong>Wind Shear (10m)</strong></td>
                  <td>{s2.wind_shear}</td>
                </tr>
                <tr>
                  <td><strong>Reconstructed Release Window</strong></td>
                  <td><strong>{s2.reconstructed_release_window}</strong></td>
                  <td><strong>Cone Uncertainty Margin</strong></td>
                  <td>{s2.spatio_temporal_origin_cone}</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Section 3: Vessel Telemetry & Behavioral Anomalies */}
          <div className="dossier-section">
            <h4 className="section-title">SECTION III: AIS TELEMETRY & BEHAVIORAL ANOMALY EVIDENCE</h4>
            <div className="anomaly-alert-box">
              <strong>INVESTIGATIVE CORROBORATION:</strong> {s3.investigative_assessment}
            </div>
            <table className="dossier-table">
              <tbody>
                <tr>
                  <td><strong>Candidate Vessels Screened</strong></td>
                  <td>{s3.total_candidates_screened} transiting ships in shipping corridor</td>
                  <td><strong>Ruled Out via Physics</strong></td>
                  <td>{s3.candidates_ruled_out_by_physics} ships (drift impossibility)</td>
                </tr>
                <tr>
                  <td><strong>Cone Intersection Time</strong></td>
                  <td>{s3.primary_suspect_telemetry?.origin_cone_intersection_utc}</td>
                  <td><strong>Deliberate AIS Blackout</strong></td>
                  <td><strong className="text-danger">{s3.primary_suspect_telemetry?.deliberate_ais_blackout_duration}</strong></td>
                </tr>
                <tr>
                  <td><strong>Speed Deceleration Anomaly</strong></td>
                  <td><strong className="text-danger">{s3.primary_suspect_telemetry?.speed_deceleration_knots}</strong></td>
                  <td><strong>Long-Axis Course Parity</strong></td>
                  <td>{s3.primary_suspect_telemetry?.course_alignment_parity}</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Section 4: Statutory Legal Citations */}
          <div className="dossier-section">
            <h4 className="section-title">SECTION IV: APPLICABLE STATUTORY CITATIONS & MARITIME LAW</h4>
            <div className="statute-list">
              {s4.map((st, idx) => (
                <div key={idx} className="statute-item">
                  <div className="statute-name">⚖️ {st.statute}: {st.title}</div>
                  <div className="statute-summary">{st.summary}</div>
                  {st.enforcement_power && (
                    <div className="statute-power"><strong>Enforcement Power:</strong> {st.enforcement_power}</div>
                  )}
                  {st.enforcement_action && (
                    <div className="statute-power"><strong>Statutory Sanction:</strong> {st.enforcement_action}</div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Section 5: Formal Detention Order */}
          <div className="dossier-section detention-directive-box">
            <h4 className="section-title text-danger">SECTION V: FORMAL STATUTORY DETENTION ORDER & BOARDING DIRECTIVE</h4>
            <div className="directives-list">
              {s5.directives?.map((d, idx) => (
                <div key={idx} className="directive-item">{d}</div>
              ))}
            </div>

            <div className="signoff-block">
              <div className="signoff-signature">
                <div className="signature-line">COMMANDING OFFICER, POLLUTION RESPONSE TEAM</div>
                <div className="signature-sub">Indian Coast Guard • Maritime Rescue Coordination Centre</div>
                <div className="signature-status">AUTHENTICATED DIGITAL RECORD // ADMISSIBLE IN ADMIRALTY COURT</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
