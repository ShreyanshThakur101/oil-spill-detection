/**
 * Case-study API client — calls the legacy /demo endpoints used by the
 * National Intelligence dashboard. Records retain synthetic provenance.
 */
import axios from "axios";

const API_BASE =
  import.meta.env.VITE_API_BASE ||
  (import.meta.env.PROD ? "/api" : "http://localhost:8000/api");

export async function fetchScenarios() {
  const res = await axios.get(`${API_BASE}/demo/scenarios`);
  return res.data; // [{id, name, region_id, stats, ...}, ...]
}

export async function fetchRegions() {
  const res = await axios.get(`${API_BASE}/demo/regions`);
  return res.data; // {count, states, union_territories, zones: [...]}
}

export async function fetchScenario(id) {
  const res = await axios.get(`${API_BASE}/demo/scenario/${id}`);
  return res.data; // {scenario, stats, scenes, detections, vessels, drift, incidents}
}

export async function resetDemo() {
  const res = await axios.post(`${API_BASE}/demo/reset`);
  return res.data; // {status, scenarios_loaded, totals, database, ...}
}
