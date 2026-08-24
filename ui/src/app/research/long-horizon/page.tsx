"use client";

import React, { useState, useEffect } from "react";

interface ResearchSubproblem {
  id: string;
  title: string;
  statement: string;
  status: string;
}

interface ResearchProblem {
  id: string;
  project_id: string;
  title: string;
  description: string;
  status: string;
  subproblems: ResearchSubproblem[];
}

export default function LongHorizonDashboardPage() {
  const [projectId, setProjectId] = useState<string>("default-project");
  const [problemTitle, setProblemTitle] = useState<string>("Collatz Conjecture Finite Bound Analysis");
  const [problemDescription, setProblemDescription] = useState<string>("Investigate bounded trajectories of the 3n + 1 function up to 10^18.");
  const [problems, setProblems] = useState<ResearchProblem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    fetchProblems();
  }, [projectId]);

  const fetchProblems = async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/long-horizon/project/${projectId}`, {
        headers: { Authorization: "Bearer axiom-dev-token" },
      });
      if (res.ok) {
        const data = await res.json();
        setProblems(data.problems || []);
      }
    } catch (err) {
      console.error("Failed to load long-horizon problems:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProblem = async () => {
    if (!problemTitle.trim()) return;
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/v1/long-horizon/problem", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer axiom-dev-token",
        },
        body: JSON.stringify({
          project_id: projectId,
          title: problemTitle,
          description: problemDescription,
        }),
      });
      if (res.ok) {
        await fetchProblems();
      }
    } catch (err) {
      console.error("Failed to create research problem:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif", backgroundColor: "#0f172a", color: "#f8fafc", minHeight: "100vh" }}>
      <header style={{ marginBottom: "2rem", borderBottom: "1px solid #334155", paddingBottom: "1rem" }}>
        <h1 style={{ fontSize: "2rem", fontWeight: "bold", color: "#ec4899" }}>
          Long-Horizon Mathematical Research Engine
        </h1>
        <p style={{ color: "#94a3b8", fontSize: "0.95rem" }}>
          AXIOM Phase 17 Problem Decomposition, Duplicate Attempt Memory, and Research Critic Audits
        </p>
      </header>

      {/* Form */}
      <div style={{ padding: "1.5rem", backgroundColor: "#1e293b", borderRadius: "0.5rem", border: "1px solid #334155", marginBottom: "2rem" }}>
        <h2 style={{ fontSize: "1.1rem", fontWeight: "600", color: "#e2e8f0", marginBottom: "1rem" }}>
          Create Long-Horizon Research Problem
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
            placeholder="Problem Title"
            value={problemTitle}
            onChange={(e) => setProblemTitle(e.target.value)}
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
            placeholder="Problem Description..."
            value={problemDescription}
            onChange={(e) => setProblemDescription(e.target.value)}
            style={{
              padding: "0.6rem 1rem",
              borderRadius: "0.375rem",
              backgroundColor: "#0f172a",
              border: "1px solid #475569",
              color: "#fff",
            }}
          />
          <button
            onClick={handleCreateProblem}
            disabled={loading}
            style={{
              alignSelf: "flex-start",
              padding: "0.6rem 1.25rem",
              backgroundColor: "#db2777",
              color: "#fff",
              border: "none",
              borderRadius: "0.375rem",
              cursor: "pointer",
              fontWeight: "600",
            }}
          >
            Decompose into Subproblems & Initialize Research Loop
          </button>
        </div>
      </div>

      {/* Problems List */}
      <h2 style={{ fontSize: "1.25rem", fontWeight: "600", color: "#cbd5e1", marginBottom: "1rem" }}>
        Research Problems ({problems.length})
      </h2>

      {loading && problems.length === 0 ? (
        <div style={{ color: "#94a3b8", textAlign: "center", padding: "2rem" }}>Loading long-horizon problems...</div>
      ) : problems.length === 0 ? (
        <div style={{ color: "#64748b" }}>No long-horizon research problems created yet.</div>
      ) : (
        <div style={{ display: "grid", gap: "1.5rem" }}>
          {problems.map((prob) => (
            <div key={prob.id} style={{ padding: "1.5rem", backgroundColor: "#1e293b", borderRadius: "0.5rem", border: "1px solid #334155" }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
                <h3 style={{ fontSize: "1.1rem", fontWeight: "bold", color: "#f8fafc" }}>{prob.title}</h3>
                <span style={{ fontSize: "0.75rem", padding: "0.2rem 0.6rem", borderRadius: "0.25rem", backgroundColor: "#0f172a", color: "#ec4899" }}>
                  {prob.status}
                </span>
              </div>
              <p style={{ color: "#94a3b8", fontSize: "0.9rem", marginBottom: "1rem" }}>{prob.description}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
