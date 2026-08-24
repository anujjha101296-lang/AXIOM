"use client";

import React, { useState, useEffect } from "react";

interface MissionBudget {
  max_iterations: number;
  max_time_sec: number;
  used_iterations: number;
  used_time_sec: number;
}

interface ResearchMission {
  id: string;
  project_id: string;
  name: string;
  objective: string;
  state: string;
  current_iteration: number;
  budget: MissionBudget;
}

export default function MissionControlDashboardPage() {
  const [projectId, setProjectId] = useState<string>("default-project");
  const [missionName, setMissionName] = useState<string>("Collatz Mission 1");
  const [missionObjective, setMissionObjective] = useState<string>("Systematic search and formal verification of 3n+1 orbits.");
  const [missions, setMissions] = useState<ResearchMission[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    fetchMissions();
  }, [projectId]);

  const fetchMissions = async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/missions/project/${projectId}`, {
        headers: { Authorization: "Bearer axiom-dev-token" },
      });
      if (res.ok) {
        const data = await res.json();
        setMissions(data.missions || []);
      }
    } catch (err) {
      console.error("Failed to load research missions:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateMission = async () => {
    if (!missionName.trim()) return;
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/v1/missions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer axiom-dev-token",
        },
        body: JSON.stringify({
          project_id: projectId,
          name: missionName,
          objective: missionObjective,
        }),
      });
      if (res.ok) {
        await fetchMissions();
      }
    } catch (err) {
      console.error("Failed to create mission:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (missionId: string, action: "start" | "pause" | "emergency-stop") => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/missions/${missionId}/${action}`, {
        method: "POST",
        headers: { Authorization: "Bearer axiom-dev-token" },
      });
      if (res.ok) {
        await fetchMissions();
      }
    } catch (err) {
      console.error(`Failed to ${action} mission:`, err);
    }
  };

  const getStateColor = (state: string) => {
    switch (state) {
      case "RUNNING":
        return "#4ade80";
      case "PAUSED":
        return "#38bdf8";
      case "EMERGENCY_STOPPED":
      case "BUDGET_EXCEEDED":
        return "#ef4444";
      default:
        return "#94a3b8";
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif", backgroundColor: "#0f172a", color: "#f8fafc", minHeight: "100vh" }}>
      <header style={{ marginBottom: "2rem", borderBottom: "1px solid #334155", paddingBottom: "1rem" }}>
        <h1 style={{ fontSize: "2rem", fontWeight: "bold", color: "#10b981" }}>
          Autonomous Research Mission Control
        </h1>
        <p style={{ color: "#94a3b8", fontSize: "0.95rem" }}>
          AXIOM Phase 19 Controlled Autonomous Research, Budget Bounds, and Emergency Stop Controls
        </p>
      </header>

      {/* Form */}
      <div style={{ padding: "1.5rem", backgroundColor: "#1e293b", borderRadius: "0.5rem", border: "1px solid #334155", marginBottom: "2rem" }}>
        <h2 style={{ fontSize: "1.1rem", fontWeight: "600", color: "#e2e8f0", marginBottom: "1rem" }}>
          Initialize New Controlled Research Mission
        </h2>
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <input
            type="text"
            placeholder="Project ID"
            value={projectId}
            onChange={(e) => setProjectId(e.target.value)}
            style={{
              padding: "0.6rem 1rem",
              borderRadius: "0.375rem",
              backgroundColor: "#0f172a",
              border: "1px solid #475569",
              color: "#fff",
            }}
          />
          <input
            type="text"
            placeholder="Mission Name"
            value={missionName}
            onChange={(e) => setMissionName(e.target.value)}
            style={{
              padding: "0.6rem 1rem",
              borderRadius: "0.375rem",
              backgroundColor: "#0f172a",
              border: "1px solid #475569",
              color: "#fff",
            }}
          />
          <textarea
            rows={3}
            placeholder="Mission Objective..."
            value={missionObjective}
            onChange={(e) => setMissionObjective(e.target.value)}
            style={{
              padding: "0.6rem 1rem",
              borderRadius: "0.375rem",
              backgroundColor: "#0f172a",
              border: "1px solid #475569",
              color: "#fff",
            }}
          />
          <button
            onClick={handleCreateMission}
            disabled={loading}
            style={{
              alignSelf: "flex-start",
              padding: "0.6rem 1.25rem",
              backgroundColor: "#059669",
              color: "#fff",
              border: "none",
              borderRadius: "0.375rem",
              cursor: "pointer",
              fontWeight: "600",
            }}
          >
            Initialize Mission with Strict Budget Bounds
          </button>
        </div>
      </div>

      {/* Missions List */}
      <h2 style={{ fontSize: "1.25rem", fontWeight: "600", color: "#cbd5e1", marginBottom: "1rem" }}>
        Active Missions ({missions.length})
      </h2>

      {loading && missions.length === 0 ? (
        <div style={{ color: "#94a3b8", textAlign: "center", padding: "2rem" }}>Loading research missions...</div>
      ) : missions.length === 0 ? (
        <div style={{ color: "#64748b" }}>No active research missions initialized.</div>
      ) : (
        <div style={{ display: "grid", gap: "1.5rem" }}>
          {missions.map((m) => (
            <div key={m.id} style={{ padding: "1.5rem", backgroundColor: "#1e293b", borderRadius: "0.5rem", border: "1px solid #334155" }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
                <h3 style={{ fontSize: "1.1rem", fontWeight: "bold", color: "#f8fafc" }}>{m.name}</h3>
                <span style={{ fontSize: "0.75rem", padding: "0.2rem 0.6rem", borderRadius: "0.25rem", backgroundColor: "#0f172a", color: getStateColor(m.state) }}>
                  {m.state}
                </span>
              </div>
              <p style={{ color: "#94a3b8", fontSize: "0.9rem", marginBottom: "1rem" }}>{m.objective}</p>

              <div style={{ display: "flex", gap: "1rem" }}>
                <button
                  onClick={() => handleAction(m.id, "start")}
                  style={{ padding: "0.4rem 0.8rem", backgroundColor: "#16a34a", color: "#fff", border: "none", borderRadius: "0.25rem", cursor: "pointer", fontSize: "0.85rem" }}
                >
                  Start / Resume
                </button>
                <button
                  onClick={() => handleAction(m.id, "pause")}
                  style={{ padding: "0.4rem 0.8rem", backgroundColor: "#0284c7", color: "#fff", border: "none", borderRadius: "0.25rem", cursor: "pointer", fontSize: "0.85rem" }}
                >
                  Pause
                </button>
                <button
                  onClick={() => handleAction(m.id, "emergency-stop")}
                  style={{ padding: "0.4rem 0.8rem", backgroundColor: "#dc2626", color: "#fff", border: "none", borderRadius: "0.25rem", cursor: "pointer", fontSize: "0.85rem", fontWeight: "bold" }}
                >
                  EMERGENCY STOP
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
