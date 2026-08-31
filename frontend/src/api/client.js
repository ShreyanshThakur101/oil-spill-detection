import axios from "axios";

const API_BASE = "http://localhost:8000/api";

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
