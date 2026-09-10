import axios from "axios";

// Automatically adapts to Vercel deployment, custom environment variable, or local dev
const API_BASE =
  import.meta.env.VITE_API_BASE ||
  (import.meta.env.PROD ? "/api" : "http://localhost:8000/api");

export async function listCases() {
  const res = await axios.get(`${API_BASE}/cases`);
  return res.data;
}

export async function getCase(caseId) {
  const res = await axios.get(`${API_BASE}/cases/${caseId}`);
  return res.data;
}

export async function runPipeline(caseId) {
  const res = await axios.post(`${API_BASE}/cases/${caseId}/run`);
  return res.data;
}

export async function getDossier(caseId, mmsi = null) {
  const url = mmsi ? `${API_BASE}/cases/${caseId}/dossier?mmsi=${mmsi}` : `${API_BASE}/cases/${caseId}/dossier`;
  const res = await axios.post(url);
  return res.data;
}

export async function getNugenBenchmark() {
  const res = await axios.get(`${API_BASE}/nugen/benchmark`);
  return res.data;
}

export async function runNugenInference(payload) {
  const res = await axios.post(`${API_BASE}/nugen/inference`, payload);
  return res.data;
}
