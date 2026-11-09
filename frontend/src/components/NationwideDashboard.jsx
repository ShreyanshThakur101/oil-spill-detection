import React, { useEffect, useRef, useState } from "react";
import { useDemo } from "../context/DemoContext";
import ScenarioSelector from "./ScenarioSelector";
import NationwideMap from "./NationwideMap";

function fmtTime(value) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toISOString().replace("T", " ").slice(0, 16) + " UTC";
}

function bboxFromGeoJSON(geojson) {
  try {
    const coords = geojson?.geometry?.coordinates?.[0] || [];
    const lons = coords.map((p) => p[0]);
    const lats = coords.map((p) => p[1]);
    return [Math.min(...lons), Math.min(...lats), Math.max(...lons), Math.max(...lats)];
  } catch {
    return null;
  }
}

function severityClass(severity) {
  if (severity === "CRITICAL") return "sev-critical";
  if (severity === "HIGH") return "sev-high";
  return "sev-medium";
}

function statusClass(status) {
  return String(status).toUpperCase() === "OPEN" ? "status-open" : "status-review";
}

function formatStatus(status) {
  return String(status || "—").replaceAll("_", " ");
}

function polygonCenter(detections) {
  const ring = detections?.[0]?.polygon?.geometry?.coordinates?.[0];
  if (!Array.isArray(ring) || ring.length === 0) return null;
  const points = ring.filter(
    (point) =>
      Array.isArray(point) &&
      Number.isFinite(point[0]) &&
      Number.isFinite(point[1])
  );
  if (points.length === 0) return null;
  const lon = points.reduce((sum, point) => sum + point[0], 0) / points.length;
  const lat = points.reduce((sum, point) => sum + point[1], 0) / points.length;
  return {
    lat,
    lon,
    label: `${Math.abs(lat).toFixed(2)}°${lat >= 0 ? "N" : "S"}, ${Math.abs(lon).toFixed(2)}°${lon >= 0 ? "E" : "W"}`,
  };
}

function RecordChip({ full = false }) {
  return (
    <span
      className="record-chip"
      title="Illustrative synthetic record — not verified operational evidence"
    >
      {full ? "ILLUSTRATIVE CASE STUDY" : "ILLUSTRATIVE"}
    </span>
  );
}

function StatTile({ label, value, accent = "#38bdf8", sub }) {
  return (
    <div className="stat-tile">
      <span className="stat-value" style={{ color: accent }}>
        {value}
      </span>
      <span className="stat-label">{label}</span>
      {sub && <span className="stat-sub">{sub}</span>}
    </div>
  );
}

export default function NationwideDashboard() {
  const {
    scenarios,
    regions,
    regionStats,
    selectedScenario,
    selectedScenarioMeta,
    scenarioData,
    selectScenario,
    resetInfo,
    loading,
    error,
  } = useDemo();

  const [coastFilter, setCoastFilter] = useState("ALL");
  const [typeFilter, setTypeFilter] = useState("ALL");
  const [focusBounds, setFocusBounds] = useState(null);
  const [resetToken, setResetToken] = useState(0);
  const [tab, setTab] = useState("overview");
  const [incidentFilter, setIncidentFilter] = useState("ALL");
  const [focusedZone, setFocusedZone] = useState(null);
  const lastScenarioRef = useRef(null);

  // Focus the map whenever the user actively switches scenario.
  useEffect(() => {
    const scenario = scenarioData?.scenario;
    if (!scenario?.id) return;
    if (lastScenarioRef.current === null) {
      lastScenarioRef.current = scenario.id;
      return;
    }
    if (lastScenarioRef.current !== scenario.id) {
      lastScenarioRef.current = scenario.id;
      setFocusBounds(scenario.bbox);
      setFocusedZone(null);
    }
  }, [scenarioData]);

  const scenario = scenarioData?.scenario || selectedScenarioMeta || null;
  const stats = scenarioData?.stats || scenario?.stats || {};
  const detections = scenarioData?.detections || [];
  const vessels = scenarioData?.vessels || [];
  const drift = scenarioData?.drift || [];
  const incidents = scenarioData?.incidents || [];
  const scenes = scenarioData?.scenes || [];

  const orderedScenes = scenes
    .slice()
    .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
  const firstScene = orderedScenes[0];
  const lastScene = orderedScenes[orderedScenes.length - 1];
  const detectionCenter = polygonCenter(detections);
  const topVessel = vessels.slice().sort((a, b) => (a.rank || 99) - (b.rank || 99))[0];
  const openIncidents = incidents.filter(
    (incident) => String(incident.status).toUpperCase() === "OPEN"
  ).length;
  const reviewIncidents = incidents.filter(
    (incident) => String(incident.status).toUpperCase() === "UNDER_REVIEW"
  ).length;
  const maxDriftUncertainty = drift.reduce(
    (max, item) => Math.max(max, Number(item.uncertainty_km) || 0),
    0
  );
  const sensorList =
    [...new Set(scenes.map((scene) => scene.sensor).filter(Boolean))].join(" / ") || "—";
  const polarizationList =
    [...new Set(scenes.map((scene) => scene.polarization).filter(Boolean))].join(" / ") || "—";

  const zoneById = Object.fromEntries(regions.map((z) => [z.id, z]));
  const vesselById = Object.fromEntries(vessels.map((v) => [v.vessel_id, v]));
  const detectionById = Object.fromEntries(detections.map((d) => [d.id, d]));
  const scenarioByRegion = Object.fromEntries(
    scenarios.filter((s) => s.region_id).map((s) => [s.region_id, s])
  );

  const totalCoastline = regions.reduce((sum, z) => sum + (z.coastline_km || 0), 0);

  const filteredRegions = regions.filter((zone) => {
    if (coastFilter !== "ALL" && zone.coast !== coastFilter) return false;
    if (typeFilter !== "ALL" && zone.type !== typeFilter) return false;
    return true;
  });

  const filteredIncidents = incidents.filter((incident) => {
    if (incidentFilter === "ALL") return true;
    return String(incident.status).toUpperCase() === incidentFilter;
  });

  function focusZone(zone) {
    const scenarioForZone = scenarioByRegion[zone.id];
    if (scenarioForZone && scenarioForZone.id !== selectedScenario) {
      selectScenario(scenarioForZone.id);
      setTab("overview");
    }
    setFocusedZone(zone.id);
    setFocusBounds(zone.bbox);
  }

  function focusPoint(position) {
    if (!position?.lat || !position?.lon) return;
    const pad = 0.06;
    setFocusBounds([
      position.lon - pad,
      position.lat - pad,
      position.lon + pad,
      position.lat + pad,
    ]);
    setFocusedZone(null);
  }

  function focusDrift(item) {
    const bbox = bboxFromGeoJSON(item.origin_polygon);
    if (bbox) setFocusBounds(bbox);
    setFocusedZone(null);
  }

  function nationalView() {
    setFocusBounds(null);
    setFocusedZone(null);
    setResetToken((token) => token + 1);
  }

  const tabs = [
    ["overview", "Overview"],
    ["detections", "Slick Analysis"],
    ["vessels", "Attribution"],
    ["incidents", "Investigations"],
    ["drift", "Drift Analysis"],
  ];

  return (
    <div className="national-layout">
      {/* ------------------------------------------------------------------ */}
      {/* LEFT — 13 coastal states & UTs                                      */}
      {/* ------------------------------------------------------------------ */}
      <aside className="national-left">
        <div className="national-summary">
          <div className="panel-eyebrow">NATIONAL COASTAL COVERAGE</div>
          <div className="national-summary-grid">
            <div>
              <span className="summary-big">{regionStats.count || regions.length}</span>
              <span className="summary-small">Coastal zones</span>
            </div>
            <div>
              <span className="summary-big">{regionStats.states}</span>
              <span className="summary-small">States</span>
            </div>
            <div>
              <span className="summary-big">{regionStats.union_territories}</span>
              <span className="summary-small">Union Territories</span>
            </div>
            <div>
              <span className="summary-big">{Math.round(totalCoastline).toLocaleString()}</span>
              <span className="summary-small">Coastline km</span>
            </div>
          </div>
          <p className="national-disclaimer">
            Rectangles are provisional satellite catalog search envelopes — not
            legal or administrative boundaries.
          </p>
        </div>

        <div className="panel-heading">
          <span>13 Coastal States &amp; UTs</span>
          <span className="panel-count">{filteredRegions.length}</span>
        </div>

        <div className="filter-row">
          <select
            aria-label="Filter by coast"
            value={coastFilter}
            onChange={(e) => setCoastFilter(e.target.value)}
          >
            <option value="ALL">All coasts</option>
            <option value="WEST">West coast</option>
            <option value="EAST">East coast</option>
            <option value="ISLANDS">Islands</option>
          </select>
          <select
            aria-label="Filter by zone type"
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
          >
            <option value="ALL">States + UTs</option>
            <option value="STATE">States only</option>
            <option value="UNION_TERRITORY">UTs only</option>
          </select>
        </div>

        <div className="zone-list">
          {filteredRegions.map((zone) => {
            const caseStudy = scenarioByRegion[zone.id];
            const active = focusedZone
              ? focusedZone === zone.id
              : scenario?.region_id === zone.id;
            return (
              <button
                key={zone.id}
                type="button"
                className={`zone-card ${active ? "zone-active" : ""}`}
                onClick={() => focusZone(zone)}
                title={zone.envelope_notes}
              >
                <div className="zone-card-top">
                  <span className={`zone-dot coast-${zone.coast.toLowerCase()}`} />
                  <span className="zone-name">{zone.name}</span>
                  {caseStudy && (
                    <span
                      className="zone-case-badge"
                      title="Illustrative case study available"
                    >
                      CASE
                    </span>
                  )}
                </div>
                <div className="zone-meta">
                  <span>{zone.coast}</span>
                  <span>{zone.type === "STATE" ? "State" : "UT"}</span>
                  <span>{zone.coastline_km} km</span>
                </div>
                <div className="zone-ports">{(zone.ports || []).slice(0, 2).join(" • ")}</div>
              </button>
            );
          })}
          {filteredRegions.length === 0 && (
            <div className="empty-note">No coastal zones match these filters.</div>
          )}
        </div>
      </aside>

      {/* ------------------------------------------------------------------ */}
      {/* CENTER — nationwide map                                             */}
      {/* ------------------------------------------------------------------ */}
      <section className="national-map-column">
        <div className="national-map-toolbar">
          <div className="map-toolbar-title">
            <span className="map-dot" />
            <span>National Intelligence Dashboard</span>
            <RecordChip />
          </div>
          <button type="button" className="btn-outline-cyan" onClick={nationalView}>
            ⤢ National view
          </button>
        </div>
        <NationwideMap focusBounds={focusBounds} resetToken={resetToken} />
      </section>

      {/* ------------------------------------------------------------------ */}
      {/* RIGHT — selected scenario                                          */}
      {/* ------------------------------------------------------------------ */}
      <aside className="national-right">
        <ScenarioSelector />

        {error && <div className="panel-error">{error}</div>}

        {resetInfo && (
          <div className="reset-result">
            ✓ Case records refreshed — {resetInfo.totals?.scenes ?? 0} observation
            scenes, {resetInfo.totals?.detections ?? 0} slick detections,{" "}
            {resetInfo.totals?.vessels ?? 0} vessel assessments and{" "}
            {resetInfo.totals?.drift ?? 0} drift analyses;{" "}
            {resetInfo.totals?.incidents ?? 0} investigation records available.
          </div>
        )}

        {scenario ? (
          <>
            <div className="scenario-hero">
              <div className="scenario-hero-top">
                <div>
                  <div className="panel-eyebrow">ACTIVE CASE STUDY</div>
                  <h2>{scenario.name}</h2>
                  <div className="scenario-region">
                    {scenario.region_name || zoneById[scenario.region_id]?.name || "India"} •{" "}
                    {scenario.coast
                      ? `${scenario.coast.charAt(0)}${scenario.coast.slice(1).toLowerCase()}`
                      : "—"}{" "}
                    coast • {scenario.primary_mrcc || "—"}
                  </div>
                </div>
                <RecordChip full />
              </div>
              <p className="scenario-summary">{scenario.summary}</p>
              <div className="stat-grid">
                <StatTile
                  label="Observations"
                  value={stats.scenes ?? 0}
                  accent="#a78bfa"
                />
                <StatTile
                  label="Slick detections"
                  value={stats.detections ?? 0}
                  accent="#f87171"
                />
                <StatTile
                  label="Vessel candidates"
                  value={stats.vessels ?? 0}
                  accent="#38bdf8"
                />
                <StatTile
                  label="Investigations"
                  value={stats.incidents ?? 0}
                  accent="#fb923c"
                />
                <StatTile
                  label="Slick area"
                  value={`${stats.total_area_sqkm ?? 0} km²`}
                  accent="#facc15"
                />
                <StatTile
                  label="Top attribution"
                  value={
                    stats.top_attribution_score != null
                      ? `${Math.round(stats.top_attribution_score * 100)}%`
                      : "—"
                  }
                  accent="#06d6a0"
                />
              </div>
              <div className="methodology-note">
                <strong>Illustrative case study.</strong> All observations, vessel
                tracks, drift reconstructions and investigation records are synthetic
                data generated to exercise the analytical workflow. They do not
                describe a verified historical incident, real satellite acquisition,
                confirmed vessel identity, or completed enforcement action.
              </div>
            </div>

            <div className="detail-tabs">
              {tabs.map(([id, label]) => (
                <button
                  key={id}
                  type="button"
                  className={`detail-tab ${tab === id ? "active" : ""}`}
                  onClick={() => setTab(id)}
                >
                  {label}
                  {id === "incidents" && (
                    <span className="tab-count">{incidents.length}</span>
                  )}
                </button>
              ))}
            </div>

            <div className="detail-body">
              {tab === "overview" && (
                <div className="detail-stack">
                  <div className="detail-card">
                    <div className="detail-card-head">
                      <span>Case summary</span>
                      <RecordChip />
                    </div>
                    <dl className="kv-grid">
                      <div>
                        <dt>Location</dt>
                        <dd>
                          {[detections[0]?.sector, detectionCenter?.label]
                            .filter(Boolean)
                            .join(" · ") || scenario.region_name || "—"}
                        </dd>
                      </div>
                      <div>
                        <dt>Observation window</dt>
                        <dd>
                          {firstScene
                            ? `${fmtTime(firstScene.timestamp)} – ${fmtTime(lastScene?.timestamp)}`
                            : "—"}
                        </dd>
                      </div>
                      <div>
                        <dt>Satellite record</dt>
                        <dd>
                          {scenes.length} × {sensorList} · {polarizationList}
                        </dd>
                      </div>
                      <div>
                        <dt>Slick detection</dt>
                        <dd>
                          {detections.length} detections · {stats.total_area_sqkm ?? 0} km²
                        </dd>
                      </div>
                      <div>
                        <dt>Lead attribution</dt>
                        <dd>
                          {topVessel
                            ? `${topVessel.name} · ${Math.round((topVessel.attribution_score || 0) * 100)}%`
                            : "—"}
                        </dd>
                      </div>
                      <div>
                        <dt>Drift reconstruction</dt>
                        <dd>
                          {drift.length} analyses
                          {maxDriftUncertainty ? ` · ±${maxDriftUncertainty} km` : ""}
                        </dd>
                      </div>
                      <div>
                        <dt>Investigation status</dt>
                        <dd>
                          {incidents.length
                            ? `${openIncidents} open · ${reviewIncidents} under review`
                            : "No active investigations"}
                        </dd>
                      </div>
                      <div>
                        <dt>Record class</dt>
                        <dd>Illustrative / synthetic</dd>
                      </div>
                    </dl>
                    <details className="technical-metadata">
                      <summary>Technical metadata &amp; provenance</summary>
                      <dl className="kv-grid compact">
                        <div><dt>Case study ID</dt><dd>{scenario.id}</dd></div>
                        <div>
                          <dt>Surveillance zone</dt>
                          <dd>
                            {zoneById[scenario.region_id]?.name ||
                              scenario.region_name ||
                              scenario.region_id}
                          </dd>
                        </div>
                        <div><dt>Primary MRCC</dt><dd>{scenario.primary_mrcc || "—"}</dd></div>
                        <div>
                          <dt>Peak confidence</dt>
                          <dd>
                            {stats.max_confidence != null
                              ? `${Math.round(stats.max_confidence * 100)}%`
                              : "—"}
                          </dd>
                        </div>
                      </dl>
                      <p>
                        Generated illustrative records with synthetic provenance retained
                        in the source fixtures. Not verified historical evidence and not
                        intended for enforcement or legal use.
                      </p>
                    </details>
                  </div>

                  <div className="detail-card">
                    <div className="detail-card-head">
                      <span>Satellite observations</span>
                      <span className="muted">{scenes.length} observation records</span>
                    </div>
                    {scenes.map((scene) => (
                      <div className="mini-row" key={scene.id}>
                        <div>
                          <strong>{scene.id}</strong>
                          <div className="muted">
                            {fmtTime(scene.timestamp)} • {scene.sensor} • {scene.polarization}
                          </div>
                        </div>
                        <span className="mono-small">
                          {scene.bbox?.join(", ")}
                        </span>
                      </div>
                    ))}
                  </div>

                  <div className="detail-card">
                    <div className="detail-card-head">
                      <span>Priority investigations</span>
                      <span className="muted">{incidents.length} logged</span>
                    </div>
                    {incidents.slice(0, 2).map((incident) => (
                      <div className="incident-compact" key={incident.incident_id}>
                        <span className={`severity-dot ${severityClass(incident.severity)}`} />
                        <div>
                          <strong>{incident.title}</strong>
                          <div className="muted">
                            {incident.severity} • {formatStatus(incident.status)} •{" "}
                            {fmtTime(incident.reported_at)}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {tab === "detections" && (
                <div className="detail-stack">
                  {detections.map((det) => (
                    <div className="detail-card" key={det.id}>
                      <div className="detail-card-head">
                        <span>{det.sector || "Slick detection"}</span>
                        <RecordChip />
                      </div>
                      <div className="confidence-line">
                        <span>Detection confidence</span>
                        <strong>{Math.round((det.confidence || 0) * 100)}%</strong>
                      </div>
                      <div className="score-bar-bg">
                        <div
                          className="score-bar-fill high"
                          style={{ width: `${Math.round((det.confidence || 0) * 100)}%` }}
                        />
                      </div>
                      <dl className="kv-grid compact">
                        <div><dt>Detection ID</dt><dd>{det.id}</dd></div>
                        <div><dt>Observation</dt><dd>{det.scene_id}</dd></div>
                        <div><dt>Area</dt><dd>{det.area_sqkm} km²</dd></div>
                        <div><dt>Perimeter</dt><dd>{det.perimeter_km} km</dd></div>
                        <div><dt>Elongation</dt><dd>{det.elongation}</dd></div>
                        <div><dt>Age class</dt><dd>{det.age_class}</dd></div>
                      </dl>
                    </div>
                  ))}
                </div>
              )}

              {tab === "vessels" && (
                <div className="detail-stack">
                  {vessels
                    .slice()
                    .sort((a, b) => (a.rank || 99) - (b.rank || 99))
                    .map((vessel) => {
                      const score = vessel.attribution_score || 0;
                      return (
                        <div className="detail-card" key={vessel.vessel_id}>
                          <div className="detail-card-head">
                            <span>
                              <span className="vessel-rank">#{vessel.rank}</span>{" "}
                              {vessel.name}
                            </span>
                            <span className="flag-tag">
                              {vessel.flag_name} · {vessel.flag}
                            </span>
                          </div>
                          <div className="muted">
                            {vessel.type} • MMSI {vessel.mmsi} • {vessel.length_m} m
                          </div>
                          <div className="confidence-line">
                            <span>Attribution score</span>
                            <strong>{Math.round(score * 100)}%</strong>
                          </div>
                          <div className="score-bar-bg">
                            <div
                              className={`score-bar-fill ${
                                score >= 0.8 ? "high" : score >= 0.5 ? "medium" : "low"
                              }`}
                              style={{ width: `${Math.round(score * 100)}%` }}
                            />
                          </div>
                          <div className="telemetry-row">
                            <div className="telemetry-item">
                              <span className="telemetry-label">AIS gap</span>
                              <span className="telemetry-val">{vessel.ais_gap_minutes} min</span>
                            </div>
                            <div className="telemetry-item">
                              <span className="telemetry-label">Speed drop</span>
                              <span className="telemetry-val">{vessel.speed_drop_knots} kt</span>
                            </div>
                            <div className="telemetry-item">
                              <span className="telemetry-label">Drift overlap</span>
                              <span className="telemetry-val">
                                {Math.round((vessel.drift_overlap_confidence || 0) * 100)}%
                              </span>
                            </div>
                            <div className="telemetry-item">
                              <span className="telemetry-label">Destination</span>
                              <span className="telemetry-val">{vessel.destination}</span>
                            </div>
                          </div>
                          <div className="card-actions">
                            <span className="muted">Linked to {vessel.detection_id}</span>
                            <button
                              type="button"
                              className="btn-outline-cyan small"
                              onClick={() => focusPoint(vessel.position)}
                            >
                              Focus on map
                            </button>
                          </div>
                        </div>
                      );
                    })}
                </div>
              )}

              {tab === "incidents" && (
                <div className="detail-stack">
                  <div className="filter-row">
                    <select
                      aria-label="Filter investigations by status"
                      value={incidentFilter}
                      onChange={(e) => setIncidentFilter(e.target.value)}
                    >
                      <option value="ALL">All statuses</option>
                      <option value="OPEN">Open only</option>
                      <option value="UNDER_REVIEW">Under review</option>
                    </select>
                    <span className="muted">
                      {filteredIncidents.length} investigations
                    </span>
                  </div>
                  {filteredIncidents.map((incident) => {
                    const vessel = vesselById[incident.vessel_id];
                    const detection = detectionById[incident.detection_id];
                    return (
                      <div className="detail-card" key={incident.incident_id}>
                        <div className="detail-card-head">
                          <span>{incident.title}</span>
                          <span className={`status-pill ${statusClass(incident.status)}`}>
                            {formatStatus(incident.status)}
                          </span>
                        </div>
                        <div className="incident-tags">
                          <span className={`status-pill ${severityClass(incident.severity)}`}>
                            {incident.severity}
                          </span>
                          <span className="muted">{incident.incident_id}</span>
                          <span className="muted">{fmtTime(incident.reported_at)}</span>
                        </div>
                        <p className="incident-description">{incident.description}</p>
                        <dl className="kv-grid compact">
                          <div><dt>MRCC</dt><dd>{incident.mrcc}</dd></div>
                          <div><dt>Response asset</dt><dd>{incident.response_asset}</dd></div>
                          <div><dt>Vessel</dt><dd>{vessel?.name || incident.vessel_id}</dd></div>
                          <div><dt>Detection</dt><dd>{detection?.sector || incident.detection_id}</dd></div>
                          <div><dt>Area</dt><dd>{incident.estimated_area_sqkm} km²</dd></div>
                          <div><dt>Observation</dt><dd>{incident.scene_id}</dd></div>
                        </dl>
                        {vessel?.position && (
                          <div className="card-actions">
                            <span className="muted">Illustrative investigation record</span>
                            <button
                              type="button"
                              className="btn-outline-cyan small"
                              onClick={() => focusPoint(vessel.position)}
                            >
                              Focus on map
                            </button>
                          </div>
                        )}
                      </div>
                    );
                  })}
                  {filteredIncidents.length === 0 && (
                    <div className="empty-note">
                      No investigations match this status filter.
                    </div>
                  )}
                </div>
              )}

              {tab === "drift" && (
                <div className="detail-stack">
                  {drift.map((item) => {
                    const detection = detectionById[item.detection_id];
                    return (
                      <div className="detail-card" key={item.detection_id}>
                        <div className="detail-card-head">
                          <span>Drift reconstruction — {item.detection_id}</span>
                          <RecordChip />
                        </div>
                        <div className="drift-metrics">
                          <div>
                            <span className="drift-value">{item.uncertainty_km} km</span>
                            <span className="drift-label">Uncertainty radius</span>
                          </div>
                          <div>
                            <span className="drift-value">{item.particle_count}</span>
                            <span className="drift-label">Particles</span>
                          </div>
                          <div>
                            <span className="drift-value">{item.trajectories?.length ?? 0}</span>
                            <span className="drift-label">Trajectory fixes</span>
                          </div>
                        </div>
                        <dl className="kv-grid compact">
                          <div><dt>Estimated origin</dt><dd>{fmtTime(item.estimated_origin_time)}</dd></div>
                          <div><dt>Detection</dt><dd>{detection?.sector || item.detection_id}</dd></div>
                          <div><dt>Current</dt><dd>{item.hydrodynamics?.current_speed_knots} kt @ {item.hydrodynamics?.current_direction_deg}°</dd></div>
                          <div><dt>Wind</dt><dd>{item.hydrodynamics?.wind_speed_knots} kt @ {item.hydrodynamics?.wind_direction_deg}°</dd></div>
                          <div><dt>Window start</dt><dd>{fmtTime(item.origin_window_start)}</dd></div>
                          <div><dt>Window end</dt><dd>{fmtTime(item.origin_window_end)}</dd></div>
                        </dl>
                        <div className="card-actions">
                          <span className="muted">Lagrangian backward trajectory model</span>
                          <button
                            type="button"
                            className="btn-outline-cyan small"
                            onClick={() => focusDrift(item)}
                          >
                            Focus origin
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

              {loading && <div className="loading-note">Loading case study data…</div>}
            </div>
          </>
        ) : (
          <div className="empty-note">
            {loading ? "Loading case studies…" : "Select a case study to begin."}
          </div>
        )}
      </aside>
    </div>
  );
}
