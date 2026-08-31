import React, { useState, useEffect } from "react";
import { listCases, runPipeline } from "./api/client";
import CaseSelector from "./components/CaseSelector";
import MapView from "./components/MapView";
import SuspectList from "./components/SuspectList";
import ConfidencePanel from "./components/ConfidencePanel";

export default function App() {
  const [cases, setCases] = useState([]);
  const [selectedCaseId, setSelectedCaseId] = useState(null);
  const [pipelineResult, setPipelineResult] = useState(null);
  const [selectedMmsi, setSelectedMmsi] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchCases() {
      try {
        const data = await listCases();
        setCases(data);
        if (data.length > 0) {
          setSelectedCaseId(data[0].id);
        }
      } catch (err) {
        console.error("Failed to load cases:", err);
        setError("Unable to connect to backend API. Ensure FastAPI server is running on http://localhost:8000.");
      }
    }
    fetchCases();
  }, []);

  const handleRun = async () => {
    if (!selectedCaseId) return;
    setLoading(true);
    setError(null);
    try {
      const result = await runPipeline(selectedCaseId);
      setPipelineResult(result);
      if (result.vessels && result.vessels.length > 0) {
        setSelectedMmsi(result.vessels[0].mmsi);
      }
    } catch (err) {
      console.error("Pipeline run failed:", err);
      setError("Pipeline execution failed. Please check backend logs.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-layout">
      <header className="app-header">
        <div className="header-brand">
          <span className="brand-logo">🛰️</span>
          <div>
            <h1>Oil Spill Detection & Vessel Attribution</h1>
            <p className="subtitle">Decision Support System for Marine Pollution Enforcement</p>
          </div>
        </div>
        <div className="header-status">
          <span className="status-indicator online"></span>
          <span>System Ready</span>
        </div>
      </header>

      {error && <div className="alert-banner">{error}</div>}

      <main className="main-content">
        <div className="sidebar">
          <CaseSelector
            cases={cases}
            selectedCaseId={selectedCaseId}
            onSelectCase={setSelectedCaseId}
            onRunPipeline={handleRun}
            loading={loading}
          />

          <SuspectList
            vessels={pipelineResult?.vessels}
            selectedMmsi={selectedMmsi}
            onSelectVessel={setSelectedMmsi}
          />
        </div>

        <div className="map-column">
          <MapView
            detection={pipelineResult?.detection}
            drift={pipelineResult?.drift}
            vessels={pipelineResult?.vessels}
            selectedMmsi={selectedMmsi}
            onSelectVessel={setSelectedMmsi}
          />

          <ConfidencePanel
            detection={pipelineResult?.detection}
            drift={pipelineResult?.drift}
          />
        </div>
      </main>
    </div>
  );
}
