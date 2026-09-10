import React, { useState, useEffect } from "react";
import { listCases, runPipeline, getDossier } from "./api/client";
import CaseSelector from "./components/CaseSelector";
import MapView from "./components/MapView";
import SuspectList from "./components/SuspectList";
import ConfidencePanel from "./components/ConfidencePanel";
import LegalDossierModal from "./components/LegalDossierModal";
import NugenValidationModal from "./components/NugenValidationModal";
import EconomicsModal from "./components/EconomicsModal";
import MultiAgentModal from "./components/MultiAgentModal";

export default function App() {
  const [cases, setCases] = useState([]);
  const [selectedCaseId, setSelectedCaseId] = useState(null);
  const [pipelineResult, setPipelineResult] = useState(null);
  const [selectedMmsi, setSelectedMmsi] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Modals state
  const [activeModal, setActiveModal] = useState(null); // 'dossier', 'validation', 'economics', 'agents'
  const [currentDossier, setCurrentDossier] = useState(null);

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
      if (result.dossier) {
        setCurrentDossier(result.dossier);
      }
    } catch (err) {
      console.error("Pipeline run failed:", err);
      setError("Pipeline execution failed. Please check backend logs.");
    } finally {
      setLoading(false);
    }
  };

  // Open dossier for a specific vessel
  const handleOpenVesselDossier = async (vessel) => {
    try {
      const d = await getDossier(selectedCaseId, vessel.mmsi);
      setCurrentDossier(d);
      setActiveModal("dossier");
    } catch (err) {
      // Fallback to pipeline dossier
      if (pipelineResult?.dossier) {
        setCurrentDossier(pipelineResult.dossier);
        setActiveModal("dossier");
      }
    }
  };

  const selectedVessel = pipelineResult?.vessels?.find((v) => v.mmsi === selectedMmsi);

  return (
    <div className="app-layout">
      {/* SAGAR-DRISHTI Master Header */}
      <header className="app-header">
        <div className="header-brand">
          <div className="brand-badge-row">
            <span className="badge-pccoe">PCCOE IGC 2026 • THEME 5: OCEAN & MARINE</span>
            <span className="badge-sdg">UN SDG 13 & 14</span>
            <span className="badge-target">TARGET: ICG MRCC • DG SHIPPING • SPCB</span>
          </div>
          <div className="brand-main-row">
            <span className="brand-emblem">🛰️🌊</span>
            <div>
              <h1 className="brand-title">SAGAR-DRISHTI</h1>
              <p className="brand-subtitle">
                Physics-Informed AI for Oil Spill Detection & Vessel Attribution • Sentinel-1 SAR + OpenDrift + 6-Factor AIS + Nugen Aligned SLM
              </p>
            </div>
          </div>
        </div>

        {/* Global Action Navigation */}
        <div className="header-controls">
          <button
            className="btn btn-nav btn-dossier"
            onClick={() => setActiveModal("dossier")}
            disabled={!pipelineResult?.dossier && !currentDossier}
            title="Generate official ICG Maritime Enforcement Brief"
          >
            📜 Court-Ready Legal Dossier
          </button>
          <button
            className="btn btn-nav"
            onClick={() => setActiveModal("validation")}
            title="Empirical Scientific Validation (Base Model vs Nugen Aligned SLM)"
          >
            🔬 Scientific Validation (Nugen Lift)
          </button>
          <button
            className="btn btn-nav"
            onClick={() => setActiveModal("economics")}
            title="Operational Running Costs, Scalability & Competitive Moat"
          >
            💰 Economics & Moat (₹4–9/case)
          </button>
          <button
            className="btn btn-nav"
            onClick={() => setActiveModal("agents")}
            title="Nugen Multi-Agent Orchestration Pipeline"
          >
            🤖 Multi-Agent Pipeline
          </button>
        </div>
      </header>

      {error && <div className="alert-banner">{error}</div>}

      <main className="main-content">
        <div className="sidebar">
          <CaseSelector
            cases={cases}
            selectedCaseId={selectedCaseId}
            onSelectCase={(id) => {
              setSelectedCaseId(id);
              setPipelineResult(null);
            }}
            onRunPipeline={handleRun}
            loading={loading}
          />

          <SuspectList
            vessels={pipelineResult?.vessels}
            selectedMmsi={selectedMmsi}
            onSelectVessel={setSelectedMmsi}
            onOpenDossier={handleOpenVesselDossier}
          />
        </div>

        <div className="map-column">
          <MapView
            caseId={selectedCaseId}
            detection={pipelineResult?.detection}
            drift={pipelineResult?.drift}
            vessels={pipelineResult?.vessels}
            selectedMmsi={selectedMmsi}
            onSelectVessel={setSelectedMmsi}
          />

          <ConfidencePanel
            detection={pipelineResult?.detection}
            drift={pipelineResult?.drift}
            nugen={pipelineResult?.nugen}
          />
        </div>
      </main>

      {/* Modals */}
      {activeModal === "dossier" && (currentDossier || pipelineResult?.dossier) && (
        <LegalDossierModal
          dossier={currentDossier || pipelineResult.dossier}
          onClose={() => setActiveModal(null)}
        />
      )}

      {activeModal === "validation" && (
        <NugenValidationModal
          targetVessel={selectedVessel || pipelineResult?.vessels?.[0]}
          onClose={() => setActiveModal(null)}
        />
      )}

      {activeModal === "economics" && (
        <EconomicsModal onClose={() => setActiveModal(null)} />
      )}

      {activeModal === "agents" && (
        <MultiAgentModal
          multiAgentData={pipelineResult?.nugen?.multi_agent}
          onClose={() => setActiveModal(null)}
        />
      )}
    </div>
  );
}
