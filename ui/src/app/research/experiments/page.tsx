"use client";

import React, { useState, useEffect } from "react";

interface ExperimentRun {
  id: string;
  run_number: number;
  status: string;
  runtime_ms: number;
  stdout: string;
  stderr: string;
  input_hash: string;
  spec_hash: string;
}

interface Experiment {
  id: string;
  project_id: string;
  name: string;
  objective: string;
  code_body: string;
  status: string;
  runs: ExperimentRun[];
}

export default function ExperimentsWorkspacePage() {
  const [projectId, setProjectId] = useState<string>("default-project");
  const [name, setName] = useState<string>("Trigonometric Identity Test");
  const [code, setCode] = useState<string>(
    "import math\nn = params.get('sample_size', 1000)\nvalues = [math.sin(i * 0.01) ** 2 + math.cos(i * 0.01) ** 2 for i in range(n)]\nmean_val = sum(values) / len(values)\nresult = {'sample_size': n, 'computed_mean': mean_val, 'identity_error': abs(mean_val - 1.0)}"
  );
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    fetchExperiments();
  }, [projectId]);

  const fetchExperiments = async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/experiment/project/${projectId}`, {
        headers: { Authorization: "Bearer axiom-dev-token" },
      });
      if (res.ok) {
        const data = await res.json();
        setExperiments(data.experiments || []);
      }
    } catch (err) {
      console.error("Failed to load experiments:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDesign = async () => {
    if (!name.trim()) return;
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/v1/experiment/design", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer axiom-dev-token",
        },
        body: JSON.stringify({
          project_id: projectId,
          name,
          objective: "Controlled numerical experiment",
          code_body: code,
        }),
      });
      if (res.ok) {
        await fetchExperiments();
      }
    } catch (err) {
      console.error("Failed to design experiment:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRun = async (expId: string) => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/experiment/${expId}/run`, {
        method: "POST",
        headers: { Authorization: "Bearer axiom-dev-token" },
      });
      if (res.ok) {
        await fetchExperiments();
      }
    } catch (err) {
      console.error("Failed to run experiment:", err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "COMPLETED":
        return "#4ade80";
      case "VALIDATED":
      case "PLANNED":
        return "#38bdf8";
      case "TIMEOUT":
      case "MEMORY_LIMIT_EXCEEDED":
        return "#fbbf24";
      case "SECURITY_VIOLATION":
      case "FAILED":
        return "#f87171";
      default:
        return "#94a3b8";
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif", backgroundColor: "#0f172a", color: "#f8fafc", minHeight: "100vh" }}>
      <header style={{ marginBottom: "2rem", borderBottom: "1px solid #334155", paddingBottom: "1rem" }}>
        <h1 style={{ fontSize: "2rem", fontWeight: "bold", color: "#38bdf8" }}>
          Computational Experiment & Verification Workspace
        </h1>
        <p style={{ color: "#94a3b8", fontSize: "0.95rem" }}>
          AXIOM Phase 15 Sandboxed Computational Execution, Reproduction, and Verification Engine
        </p>
      </header>

      {/* Notice Alert */}
      <div style={{ padding: "1rem", backgroundColor: "#1e1b4b", borderRadius: "0.5rem", border: "1px solid #4338ca", marginBottom: "2rem" }}>
        <span style={{ fontWeight: "bold", color: "#818cf8" }}>EPISTEMIC LIMITATIONS NOTICE:</span>{" "}
        <span style={{ color: "#c7d2fe", fontSize: "0.9rem" }}>
          Computational observation provides empirical support bounded to tested sample sizes. Computational support does NOT constitute a formal mathematical proof.
        </span>
      </div>

      {/* Designer Form */}
      <div style={{ padding: "1.5rem", backgroundColor: "#1e293b", borderRadius: "0.5rem", border: "1px solid #334155", marginBottom: "2rem" }}>
        <h2 style={{ fontSize: "1.1rem", fontWeight: "600", color: "#e2e8f0", marginBottom: "1rem" }}>
          Design Sandboxed Experiment
        </h2>
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <div style={{ display: "flex", gap: "1rem" }}>
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
                width: "200px",
              }}
            />
            <input
              type="text"
              placeholder="Experiment Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              style={{
                flex: 1,
                padding: "0.6rem 1rem",
                borderRadius: "0.375rem",
                backgroundColor: "#0f172a",
                border: "1px solid #475569",
                color: "#fff",
              }}
            />
          </div>
          <textarea
            rows={4}
            value={code}
            onChange={(e) => setCode(e.target.value)}
            style={{
              padding: "0.8rem",
              fontFamily: "monospace",
              fontSize: "0.85rem",
              borderRadius: "0.375rem",
              backgroundColor: "#0f172a",
              border: "1px solid #475569",
              color: "#38bdf8",
            }}
          />
          <button
            onClick={handleDesign}
            disabled={loading}
            style={{
              alignSelf: "flex-start",
              padding: "0.6rem 1.25rem",
              backgroundColor: "#0284c7",
              color: "#fff",
              border: "none",
              borderRadius: "0.375rem",
              cursor: "pointer",
              fontWeight: "600",
            }}
          >
            {loading ? "Processing..." : "Design & Validate Experiment"}
          </button>
        </div>
      </div>

      {/* Experiments List */}
      <h2 style={{ fontSize: "1.25rem", fontWeight: "600", color: "#cbd5e1", marginBottom: "1rem" }}>
        Experiments ({experiments.length})
      </h2>

      {loading && experiments.length === 0 ? (
        <div style={{ color: "#94a3b8", textAlign: "center", padding: "2rem" }}>Loading computational experiments...</div>
      ) : experiments.length === 0 ? (
        <div style={{ color: "#64748b" }}>No experiments designed for this project yet.</div>
      ) : (
        <div style={{ display: "grid", gap: "1.5rem" }}>
          {experiments.map((exp) => (
            <div key={exp.id} style={{ padding: "1.5rem", backgroundColor: "#1e293b", borderRadius: "0.5rem", border: "1px solid #334155", borderLeft: `5px solid ${getStatusColor(exp.status)}` }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                <span style={{ fontSize: "0.75rem", fontWeight: "bold", padding: "0.2rem 0.6rem", borderRadius: "0.25rem", backgroundColor: "#0f172a", color: getStatusColor(exp.status) }}>
                  EXPERIMENT • {exp.status}
                </span>
                <button
                  onClick={() => handleRun(exp.id)}
                  disabled={loading}
                  style={{
                    padding: "0.4rem 0.8rem",
                    backgroundColor: "#16a34a",
                    color: "#fff",
                    border: "none",
                    borderRadius: "0.25rem",
                    cursor: "pointer",
                    fontSize: "0.8rem",
                    fontWeight: "600",
                  }}
                >
                  Run in Sandbox
                </button>
              </div>

              <h3 style={{ fontSize: "1.15rem", fontWeight: "bold", color: "#f8fafc", marginBottom: "0.25rem" }}>
                {exp.name}
              </h3>
              <p style={{ color: "#94a3b8", fontSize: "0.85rem", marginBottom: "1rem" }}>
                {exp.objective}
              </p>

              {/* Code display */}
              <pre style={{ padding: "0.8rem", backgroundColor: "#0f172a", borderRadius: "0.375rem", fontSize: "0.8rem", color: "#38bdf8", overflowX: "auto" }}>
                {exp.code_body}
              </pre>

              {/* Runs */}
              {exp.runs && exp.runs.length > 0 && (
                <div style={{ marginTop: "1rem", borderTop: "1px solid #334155", paddingTop: "0.75rem" }}>
                  <div style={{ fontSize: "0.85rem", fontWeight: "bold", color: "#e2e8f0", marginBottom: "0.5rem" }}>
                    Execution History ({exp.runs.length} runs):
                  </div>
                  {exp.runs.map((r) => (
                    <div key={r.id} style={{ fontSize: "0.8rem", color: "#94a3b8", marginBottom: "0.25rem" }}>
                      Run #{r.run_number}: <span style={{ color: getStatusColor(r.status) }}>{r.status}</span> ({r.runtime_ms}ms, Hash: {r.spec_hash})
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
