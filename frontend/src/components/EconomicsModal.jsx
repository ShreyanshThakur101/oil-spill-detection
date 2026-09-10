import React from "react";

export default function EconomicsModal({ onClose }) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-container economics-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header-bar">
          <div className="modal-title-group">
            <span className="badge badge-success">METRICS & SCALABILITY</span>
            <h3>Operational Economics & Competitive Moat</h3>
          </div>
          <button className="btn btn-secondary" onClick={onClose}>✕ Close</button>
        </div>

        <div className="modal-body">
          {/* Top 3 Impact Numbers */}
          <div className="economics-stats-grid">
            <div className="econ-stat-box">
              <span className="stat-number text-success">₹4 – 9</span>
              <span className="stat-label">PER INCIDENT COMPUTE</span>
              <span className="stat-detail">Total cloud compute for U-Net CNN + 200-particle OpenDrift simulation.</span>
            </div>
            <div className="econ-stat-box">
              <span className="stat-number text-primary">&lt; 90 MIN</span>
              <span className="stat-label">END-TO-END TURNAROUND</span>
              <span className="stat-detail">From satellite pass to court-ready attribution dossier (vs 5–7 days manual review).</span>
            </div>
            <div className="econ-stat-box">
              <span className="stat-number text-warning">₹9,000+ CR</span>
              <span className="stat-label">LIABILITY UNLOCKED</span>
              <span className="stat-detail">Statutory damage recovery capacity illustrated by MSC Elsa III claims off Kerala.</span>
            </div>
          </div>

          {/* ROI Comparison vs Indian Coast Guard Dornier Sortie */}
          <div className="roi-comparison-banner">
            <div className="roi-icon">✈️ vs 🛰️</div>
            <div className="roi-text">
              <h4>Astronomical ROI for Indian Coast Guard Maritime Command</h4>
              <p>
                A single Indian Coast Guard aerial reconnaissance flight by a Dornier 228 maritime patrol aircraft
                costs <strong>₹35,00,000+</strong> in aviation jet fuel, crew deployment, and airframe flight hours.
                <strong> SAGAR-DRISHTI</strong> provides 24/7 automated EEZ screening and court-ready attribution at{" "}
                <strong>&lt;0.01% of the cost (₹4–9 per case)</strong> with zero data licensing fees.
              </p>
            </div>
          </div>

          {/* Operational Running Cost Breakdown */}
          <div className="cost-breakdown-section">
            <h4 className="section-title">INDIAN EEZ OPERATIONAL RUNNING COST ARCHITECTURE</h4>
            <div className="cost-cards-grid">
              <div className="cost-card">
                <h5>Always-On Cloud Infrastructure</h5>
                <p className="cost-val">~₹2,600 / month ($30/mo)</p>
                <small>FastAPI microservices + SQLite in-memory spatial joins + Vector tile server on AWS Spot/Render.</small>
              </div>
              <div className="cost-card">
                <h5>Dynamic Incident Compute</h5>
                <p className="cost-val">₹4 – 9 / incident case</p>
                <small>U-Net segmentation (&lt;5s) + 200-particle OpenDrift Lagrangian backtrack takes 2–3 min compute.</small>
              </div>
              <div className="cost-card">
                <h5>Data Licensing Fees</h5>
                <p className="cost-val text-success">₹0 / month (Zero Cost)</p>
                <small>Exclusively open scientific feeds: Copernicus Sentinel-1 SAR, CMEMS currents, ERA5 winds, GFW AIS.</small>
              </div>
              <div className="cost-card">
                <h5>Nationwide Deployment (50–100 cases/mo)</h5>
                <p className="cost-val text-primary">&lt; ₹9,000 / month total</p>
                <small>Scalable to monitor all 11,000 km of Indian coastline & 2.02M km² Exclusive Economic Zone.</small>
              </div>
            </div>
          </div>

          {/* Competitive Moat Matrix */}
          <div className="competitive-matrix-section">
            <h4 className="section-title">COMPETITIVE ANALYSIS MATRIX</h4>
            <table className="matrix-table">
              <thead>
                <tr>
                  <th>Evaluation Criteria</th>
                  <th>Cerulean / SkyTruth</th>
                  <th>Commercial (Spire/Orbital)</th>
                  <th>Generic Hackathon AI</th>
                  <th className="highlight-col">SAGAR-DRISHTI (Ours)</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>Slick Origin Estimation</strong></td>
                  <td>Static window (~8h fixed), ignores ocean currents</td>
                  <td>Proprietary, expensive cloud black-box</td>
                  <td>None (purely points at current slick)</td>
                  <td className="highlight-col"><strong>Backward Lagrangian Drift (OpenDrift + CMEMS + ERA5)</strong></td>
                </tr>
                <tr>
                  <td><strong>AIS Attribution Logic</strong></td>
                  <td>Unfused 3 separate scores; no anomaly detection</td>
                  <td>Opaque scoring; requires paid transponder feed</td>
                  <td>Nearest ship in radius (high false positives)</td>
                  <td className="highlight-col"><strong>6-Factor Weighted Heuristic + AIS Transponder Blackout Flag</strong></td>
                </tr>
                <tr>
                  <td><strong>Indian EEZ & Monsoon Tuning</strong></td>
                  <td>No Indian corridor tuning or monsoon current priors</td>
                  <td>Generic global lanes; very high latency in India</td>
                  <td>Zero domain knowledge or local sea awareness</td>
                  <td className="highlight-col"><strong>Tuned for Arabian Sea & Bay of Bengal currents + ICG SOPs</strong></td>
                </tr>
                <tr>
                  <td><strong>Legal & Decision Support</strong></td>
                  <td>Public awareness map only; no legal briefs</td>
                  <td>Raw CSV / telemetry export; no statutory reasoning</td>
                  <td>Generic ChatGPT chatbot (hallucinates statutes)</td>
                  <td className="highlight-col"><strong>Nugen Aligned Maritime SLM (Court-Ready ICG Dossiers)</strong></td>
                </tr>
                <tr>
                  <td><strong>Operational Cost / Scalability</strong></td>
                  <td>Free global public viewer; not custom deployable</td>
                  <td>$50,000+/year license; restrictive commercial data</td>
                  <td>Dependent on paid LLM APIs; not deployable</td>
                  <td className="highlight-col"><strong>Free scientific feeds + ₹4–9/case serverless compute</strong></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
