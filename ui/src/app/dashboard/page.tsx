"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { axiomApi } from "../../lib/api";

export default function DashboardPage() {
  const [projects, setProjects] = useState<any[]>([]);
  const [missions, setMissions] = useState<any[]>([]);
  const [events, setEvents] = useState<any[]>([]);
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const projData = await axiomApi.getProjects().catch(() => ({ projects: [] }));
      setProjects(projData.projects || []);

      const evtData = await axiomApi.getDomainEvents().catch(() => ({ events: [] }));
      setEvents(evtData.events || []);

      const resData = await axiomApi.getEvaluationResults().catch(() => ({ runs: [] }));
      setResults(resData.runs || []);

      if (projData.projects && projData.projects.length > 0) {
        const missData = await axiomApi.getMissions(projData.projects[0].id).catch(() => ({ missions: [] }));
        setMissions(missData.missions || []);
      }
    } catch (err) {
      console.error("Error loading dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ fontFamily: "sans-serif", backgroundColor: "#090d16", color: "#f8fafc", minHeight: "100vh", padding: "2rem" }}>
      {/* Navigation Header */}
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem", borderBottom: "1px solid #1e293b", paddingBottom: "1rem" }}>
        <div>
          <h1 style={{ fontSize: "1.75rem", fontWeight: "bold", color: "#f8fafc" }}>AXIOM Research Dashboard</h1>
          <p style={{ color: "#94a3b8", fontSize: "0.9rem" }}>Real-time telemetry and control plane for active research programs</p>
        </div>
        <div style={{ display: "flex", gap: "1rem" }}>
          <Link href="/research/mission-control" style={{ padding: "0.5rem 1rem", backgroundColor: "#6366f1", color: "#fff", borderRadius: "0.375rem", textDecoration: "none", fontSize: "0.85rem", fontWeight: "600" }}>
            + New Mission
          </Link>
          <Link href="/settings" style={{ padding: "0.5rem 1rem", backgroundColor: "#1e293b", color: "#e2e8f0", borderRadius: "0.375rem", textDecoration: "none", fontSize: "0.85rem", border: "1px solid #334155" }}>
            Settings
          </Link>
        </div>
      </header>

      {/* Main Metric Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "1.25rem", marginBottom: "2.5rem" }}>
        <div style={{ padding: "1.25rem", backgroundColor: "#0f172a", borderRadius: "0.5rem", border: "1px solid #1e293b" }}>
          <div style={{ color: "#94a3b8", fontSize: "0.8rem", textTransform: "uppercase", fontWeight: "bold" }}>Active Projects</div>
          <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#6366f1", marginTop: "0.5rem" }}>{projects.length}</div>
        </div>

        <div style={{ padding: "1.25rem", backgroundColor: "#0f172a", borderRadius: "0.5rem", border: "1px solid #1e293b" }}>
          <div style={{ color: "#94a3b8", fontSize: "0.8rem", textTransform: "uppercase", fontWeight: "bold" }}>Research Missions</div>
          <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#38bdf8", marginTop: "0.5rem" }}>{missions.length}</div>
        </div>

        <div style={{ padding: "1.25rem", backgroundColor: "#0f172a", borderRadius: "0.5rem", border: "1px solid #1e293b" }}>
          <div style={{ color: "#94a3b8", fontSize: "0.8rem", textTransform: "uppercase", fontWeight: "bold" }}>Domain Events</div>
          <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#a855f7", marginTop: "0.5rem" }}>{events.length}</div>
        </div>

        <div style={{ padding: "1.25rem", backgroundColor: "#0f172a", borderRadius: "0.5rem", border: "1px solid #1e293b" }}>
          <div style={{ color: "#94a3b8", fontSize: "0.8rem", textTransform: "uppercase", fontWeight: "bold" }}>Benchmark Runs</div>
          <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#4ade80", marginTop: "0.5rem" }}>{results.length}</div>
        </div>
      </div>

      {/* Grid Content */}
      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "2rem" }}>
        {/* Left: Active Missions */}
        <div style={{ padding: "1.5rem", backgroundColor: "#0f172a", borderRadius: "0.5rem", border: "1px solid #1e293b" }}>
          <h2 style={{ fontSize: "1.1rem", fontWeight: "bold", color: "#e2e8f0", marginBottom: "1rem" }}>
            Recent Research Missions
          </h2>

          {loading ? (
            <div style={{ color: "#94a3b8", padding: "1rem 0" }}>Loading real backend data...</div>
          ) : missions.length === 0 ? (
            <div style={{ color: "#64748b", padding: "1.5rem 0", textAlign: "center", backgroundColor: "#090d16", borderRadius: "0.375rem" }}>
              No research missions initialized. <Link href="/research/mission-control" style={{ color: "#818cf8" }}>Create your first mission</Link>.
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              {missions.map((m) => (
                <div key={m.id} style={{ padding: "1rem", backgroundColor: "#1e293b", borderRadius: "0.375rem", border: "1px solid #334155", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div>
                    <div style={{ fontWeight: "bold", color: "#f8fafc" }}>{m.name}</div>
                    <div style={{ color: "#94a3b8", fontSize: "0.85rem" }}>{m.objective}</div>
                  </div>
                  <span style={{ fontSize: "0.75rem", padding: "0.2rem 0.6rem", borderRadius: "0.25rem", backgroundColor: "#090d16", color: m.state === "RUNNING" ? "#4ade80" : "#38bdf8" }}>
                    {m.state}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right: Quick Nav & Audit Feed */}
        <div style={{ padding: "1.5rem", backgroundColor: "#0f172a", borderRadius: "0.5rem", border: "1px solid #1e293b" }}>
          <h2 style={{ fontSize: "1.1rem", fontWeight: "bold", color: "#e2e8f0", marginBottom: "1rem" }}>
            Control Plane Navigation
          </h2>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", fontSize: "0.9rem" }}>
            <Link href="/research/mission-control" style={{ padding: "0.75rem", backgroundColor: "#1e293b", color: "#818cf8", borderRadius: "0.375rem", textDecoration: "none", fontWeight: "bold" }}>
              🎯 Autonomous Mission Control
            </Link>
            <Link href="/research/formal" style={{ padding: "0.75rem", backgroundColor: "#1e293b", color: "#cbd5e1", borderRadius: "0.375rem", textDecoration: "none" }}>
              ∴ Formal Proof Verification
            </Link>
            <Link href="/research/experiments" style={{ padding: "0.75rem", backgroundColor: "#1e293b", color: "#cbd5e1", borderRadius: "0.375rem", textDecoration: "none" }}>
              ⚗ Computational Experiments
            </Link>
            <Link href="/research/graph" style={{ padding: "0.75rem", backgroundColor: "#1e293b", color: "#cbd5e1", borderRadius: "0.375rem", textDecoration: "none" }}>
              🕸 Epistemic Knowledge Graph
            </Link>
            <Link href="/research/benchmarks" style={{ padding: "0.75rem", backgroundColor: "#1e293b", color: "#cbd5e1", borderRadius: "0.375rem", textDecoration: "none" }}>
              📊 Challenge Harness Benchmarks
            </Link>
            <Link href="/research/control-plane" style={{ padding: "0.75rem", backgroundColor: "#1e293b", color: "#cbd5e1", borderRadius: "0.375rem", textDecoration: "none" }}>
              ⚡ Production Control Plane
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
