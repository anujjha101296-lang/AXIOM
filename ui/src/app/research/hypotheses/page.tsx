"use client";

import React, { useState, useEffect } from "react";

interface HypothesisPrediction {
  id: string;
  prediction_text: string;
  expected_observation: string;
  falsifying_observation: string;
}

interface HypothesisCritique {
  id: string;
  status: string;
  critique_text: string;
  unsupported_assumptions: string[];
}

interface VerificationPlan {
  id: string;
  question: string;
  method: string;
  success_criteria: string;
  failure_criteria: string;
  limitations: string[];
}

interface Hypothesis {
  id: string;
  project_id: string;
  claim: string;
  motivation: string;
  status: string;
  confidence_score: number;
  rationale: string;
  predictions: HypothesisPrediction[];
  critiques: HypothesisCritique[];
  verification_plan?: VerificationPlan;
}

export default function HypothesesWorkspacePage() {
  const [projectId, setProjectId] = useState<string>("default-project");
  const [question, setQuestion] = useState<string>("How does model scale affect reasoning precision?");
  const [hypotheses, setHypotheses] = useState<Hypothesis[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    fetchHypotheses();
  }, [projectId]);

  const fetchHypotheses = async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/hypothesis/project/${projectId}`, {
        headers: { Authorization: "Bearer axiom-dev-token" },
      });
      if (res.ok) {
        const data = await res.json();
        setHypotheses(data.hypotheses || []);
      }
    } catch (err) {
      console.error("Failed to load hypotheses:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!question.trim()) return;
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/v1/hypothesis/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer axiom-dev-token",
        },
        body: JSON.stringify({ project_id: projectId, question }),
      });
      if (res.ok) {
        await fetchHypotheses();
      }
    } catch (err) {
      console.error("Failed to generate hypothesis:", err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "SUPPORTED":
        return "#4ade80";
      case "WEAKLY_SUPPORTED":
        return "#a3e635";
      case "PROPOSED":
      case "UNDER_REVIEW":
        return "#38bdf8";
      case "CONTRADICTED":
        return "#fbbf24";
      case "FALSIFIED":
        return "#f87171";
      default:
        return "#94a3b8";
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif", backgroundColor: "#0f172a", color: "#f8fafc", minHeight: "100vh" }}>
      <header style={{ marginBottom: "2rem", borderBottom: "1px solid #334155", paddingBottom: "1rem" }}>
        <h1 style={{ fontSize: "2rem", fontWeight: "bold", color: "#a855f7" }}>
          Scientific Hypothesis & Reasoning Workspace
        </h1>
        <p style={{ color: "#94a3b8", fontSize: "0.95rem" }}>
          AXIOM Phase 14 Hypothesis Formulation, Critique, Falsification, and Verification Planning
        </p>
      </header>

      {/* Generator Form */}
      <div style={{ padding: "1.5rem", backgroundColor: "#1e293b", borderRadius: "0.5rem", border: "1px solid #334155", marginBottom: "2rem" }}>
        <h2 style={{ fontSize: "1.1rem", fontWeight: "600", color: "#e2e8f0", marginBottom: "1rem" }}>
          Formulate Scientific Hypothesis
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
              placeholder="Enter Research Question..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
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
          <button
            onClick={handleGenerate}
            disabled={loading}
            style={{
              alignSelf: "flex-start",
              padding: "0.6rem 1.25rem",
              backgroundColor: "#9333ea",
              color: "#fff",
              border: "none",
              borderRadius: "0.375rem",
              cursor: "pointer",
              fontWeight: "600",
            }}
          >
            {loading ? "Generating & Critiquing..." : "Generate Hypotheses & Verification Plan"}
          </button>
        </div>
      </div>

      {/* Hypotheses List */}
      <h2 style={{ fontSize: "1.25rem", fontWeight: "600", color: "#cbd5e1", marginBottom: "1rem" }}>
        Hypotheses ({hypotheses.length})
      </h2>

      {loading && hypotheses.length === 0 ? (
        <div style={{ color: "#94a3b8", textAlign: "center", padding: "2rem" }}>Evaluating research question...</div>
      ) : hypotheses.length === 0 ? (
        <div style={{ color: "#64748b" }}>No hypotheses formulated for this project yet.</div>
      ) : (
        <div style={{ display: "grid", gap: "1.5rem" }}>
          {hypotheses.map((h) => (
            <div key={h.id} style={{ padding: "1.5rem", backgroundColor: "#1e293b", borderRadius: "0.5rem", border: "1px solid #334155", borderLeft: `5px solid ${getStatusColor(h.status)}` }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                <span style={{ fontSize: "0.75rem", fontWeight: "bold", padding: "0.2rem 0.6rem", borderRadius: "0.25rem", backgroundColor: "#0f172a", color: getStatusColor(h.status) }}>
                  HYPOTHESIS • {h.status}
                </span>
                <span style={{ color: "#94a3b8", fontSize: "0.85rem" }}>
                  Confidence Score: {(h.confidence_score * 100).toFixed(0)}%
                </span>
              </div>

              <h3 style={{ fontSize: "1.15rem", fontWeight: "bold", color: "#f8fafc", marginBottom: "0.5rem" }}>
                {h.claim}
              </h3>
              <p style={{ color: "#cbd5e1", fontSize: "0.9rem", marginBottom: "1rem" }}>
                {h.motivation}
              </p>

              {/* Predictions Section */}
              {h.predictions.length > 0 && (
                <div style={{ marginBottom: "1rem", padding: "0.75rem", backgroundColor: "#0f172a", borderRadius: "0.375rem" }}>
                  <div style={{ fontSize: "0.85rem", fontWeight: "bold", color: "#38bdf8", marginBottom: "0.5rem" }}>
                    Testable Predictions & Falsifying Conditions:
                  </div>
                  {h.predictions.map((p) => (
                    <div key={p.id} style={{ fontSize: "0.85rem", color: "#94a3b8", marginBottom: "0.25rem" }}>
                      • <span style={{ color: "#e2e8f0" }}>{p.prediction_text}</span> (Falsifier: {p.falsifying_observation})
                    </div>
                  ))}
                </div>
              )}

              {/* Verification Plan */}
              {h.verification_plan && (
                <div style={{ padding: "0.75rem", backgroundColor: "#0f172a", borderRadius: "0.375rem" }}>
                  <div style={{ fontSize: "0.85rem", fontWeight: "bold", color: "#a855f7" }}>
                    Verification Strategy:
                  </div>
                  <div style={{ fontSize: "0.85rem", color: "#cbd5e1", marginTop: "0.25rem" }}>
                    Method: {h.verification_plan.method} | Success Criteria: {h.verification_plan.success_criteria}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
