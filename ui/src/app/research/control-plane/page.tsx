"use client";

import React, { useState, useEffect } from "react";

interface AgentProfile {
  id: string;
  name: string;
  role: string;
  allowed_tools: string[];
  allowed_models: string[];
  max_steps: number;
}

interface DomainEvent {
  id: string;
  event_type: string;
  actor: string;
  timestamp: string;
}

interface WorkerNode {
  id: string;
  hostname: string;
  status: string;
}

export default function ControlPlaneDashboardPage() {
  const [agents, setAgents] = useState<AgentProfile[]>([]);
  const [events, setEvents] = useState<DomainEvent[]>([]);
  const [workers, setWorkers] = useState<WorkerNode[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    fetchControlPlaneData();
  }, []);

  const fetchControlPlaneData = async () => {
    setLoading(true);
    try {
      const resAg = await fetch("http://localhost:8000/api/v1/control-plane/agents", {
        headers: { Authorization: "Bearer axiom-dev-token" },
      });
      if (resAg.ok) {
        const dataAg = await resAg.json();
        setAgents(dataAg.agents || []);
      }

      const resEv = await fetch("http://localhost:8000/api/v1/control-plane/events", {
        headers: { Authorization: "Bearer axiom-dev-token" },
      });
      if (resEv.ok) {
        const dataEv = await resEv.json();
        setEvents(dataEv.events || []);
      }

      const resWk = await fetch("http://localhost:8000/api/v1/control-plane/workers", {
        headers: { Authorization: "Bearer axiom-dev-token" },
      });
      if (resWk.ok) {
        const dataWk = await resWk.json();
        setWorkers(dataWk.workers || []);
      }
    } catch (err) {
      console.error("Failed to load control plane data:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif", backgroundColor: "#0f172a", color: "#f8fafc", minHeight: "100vh" }}>
      <header style={{ marginBottom: "2rem", borderBottom: "1px solid #334155", paddingBottom: "1rem" }}>
        <h1 style={{ fontSize: "2rem", fontWeight: "bold", color: "#6366f1" }}>
          Research Operating System / Production Control Plane
        </h1>
        <p style={{ color: "#94a3b8", fontSize: "0.95rem" }}>
          AXIOM Phase 20 Authoritative Single Source of Truth, Agent Registry, Tool Policy Engine, and Append-Only Domain Event Log
        </p>
      </header>

      {/* Agents Section */}
      <h2 style={{ fontSize: "1.25rem", fontWeight: "600", color: "#cbd5e1", marginBottom: "1rem" }}>
        Canonical Specialist Agent Profiles ({agents.length})
      </h2>

      {loading && agents.length === 0 ? (
        <div style={{ color: "#94a3b8", textAlign: "center", padding: "2rem" }}>Loading control plane agent profiles...</div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "1rem", marginBottom: "2.5rem" }}>
          {agents.map((ag) => (
            <div key={ag.id} style={{ padding: "1.25rem", backgroundColor: "#1e293b", borderRadius: "0.5rem", border: "1px solid #334155" }}>
              <div style={{ fontSize: "0.75rem", padding: "0.2rem 0.5rem", borderRadius: "0.25rem", backgroundColor: "#0f172a", color: "#818cf8", width: "max-content", marginBottom: "0.5rem" }}>
                {ag.role}
              </div>
              <h3 style={{ fontSize: "1rem", fontWeight: "bold", color: "#f8fafc", marginBottom: "0.5rem" }}>{ag.name}</h3>
              <p style={{ fontSize: "0.8rem", color: "#94a3b8" }}>
                Allowed Tools: {ag.allowed_tools.join(", ") || "None"}
              </p>
              <p style={{ fontSize: "0.8rem", color: "#64748b" }}>Max Steps: {ag.max_steps}</p>
            </div>
          ))}
        </div>
      )}

      {/* Domain Event Stream */}
      <h2 style={{ fontSize: "1.25rem", fontWeight: "600", color: "#cbd5e1", marginBottom: "1rem" }}>
        Append-Only Domain Event Bus ({events.length})
      </h2>

      {events.length === 0 ? (
        <div style={{ color: "#64748b" }}>No domain events recorded yet.</div>
      ) : (
        <div style={{ display: "grid", gap: "0.75rem" }}>
          {events.map((ev) => (
            <div key={ev.id} style={{ padding: "0.75rem 1.25rem", backgroundColor: "#1e293b", borderRadius: "0.375rem", border: "1px solid #334155", display: "flex", justifyContent: "space-between", fontSize: "0.85rem" }}>
              <span style={{ fontWeight: "bold", color: "#38bdf8" }}>[{ev.event_type}]</span>
              <span style={{ color: "#94a3b8" }}>Actor: {ev.actor}</span>
              <span style={{ color: "#64748b" }}>{ev.timestamp}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
