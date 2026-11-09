import React, { createContext, useContext, useEffect, useState } from "react";
import {
  fetchRegions,
  fetchScenarios,
  fetchScenario,
  resetDemo,
} from "../api/demo";

const DemoContext = createContext(null);

export function DemoProvider({ children }) {
  const [scenarios, setScenarios] = useState([]);
  const [regions, setRegions] = useState([]);
  const [regionStats, setRegionStats] = useState({ count: 0, states: 0, union_territories: 0 });
  const [selectedScenario, setSelectedScenario] = useState(null);
  const [scenarioData, setScenarioData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [resetInfo, setResetInfo] = useState(null);

  // Load the scenario list and the 13 coastal zones once on mount.
  useEffect(() => {
    let cancelled = false;

    async function bootstrap() {
      try {
        const [scenarioList, regionPayload] = await Promise.all([
          fetchScenarios(),
          fetchRegions(),
        ]);
        if (cancelled) return;
        setScenarios(scenarioList);
        setRegions(regionPayload.zones || []);
        setRegionStats({
          count: regionPayload.count || 0,
          states: regionPayload.states || 0,
          union_territories: regionPayload.union_territories || 0,
        });
        if (scenarioList.length > 0) {
          await selectScenario(scenarioList[0].id, { silent: true });
        }
      } catch (err) {
        if (cancelled) return;
        console.error("Failed to bootstrap national intelligence dashboard:", err);
        setError("Could not load case studies from the backend API.");
      }
    }

    bootstrap();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function refreshScenarios() {
    const scenarioList = await fetchScenarios();
    setScenarios(scenarioList);
    return scenarioList;
  }

  async function selectScenario(id, { silent = false } = {}) {
    if (!silent) setLoading(true);
    setError(null);
    try {
      const data = await fetchScenario(id);
      setSelectedScenario(id);
      setScenarioData(data);
      return data;
    } catch (err) {
      console.error("Failed to load case study:", err);
      setError(`Failed to load case study '${id}'.`);
      return null;
    } finally {
      if (!silent) setLoading(false);
    }
  }

  async function reset() {
    setLoading(true);
    setError(null);
    setResetInfo(null);
    try {
      const result = await resetDemo();
      setResetInfo(result);
      await refreshScenarios();
      if (selectedScenario) {
        await selectScenario(selectedScenario, { silent: true });
      }
      return result;
    } catch (err) {
      console.error("Case record refresh failed:", err);
      setError("Case record refresh failed. Check that the backend is running.");
      return null;
    } finally {
      setLoading(false);
    }
  }

  const selectedScenarioMeta =
    scenarios.find((s) => s.id === selectedScenario) || scenarioData?.scenario || null;

  return (
    <DemoContext.Provider
      value={{
        scenarios,
        regions,
        regionStats,
        selectedScenario,
        selectedScenarioMeta,
        scenarioData,
        selectScenario,
        refreshScenarios,
        reset,
        resetInfo,
        loading,
        error,
      }}
    >
      {children}
    </DemoContext.Provider>
  );
}

export function useDemo() {
  const ctx = useContext(DemoContext);
  if (!ctx) throw new Error("useDemo must be used inside <DemoProvider>");
  return ctx;
}
