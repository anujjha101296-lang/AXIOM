"use client";

import React, { useState, useEffect } from "react";

interface FormalProof {
  id: string;
  proof_script: string;
  verifier_output: string;
  compiler_version: string;
  status: string;
  is_sorry_free: boolean;
}

interface FormalTheorem {
  id: string;
  project_id: string;
  name: string;
  natural_language: string;
  formal_statement: string;
  language: string;
  status: string;
  proofs: FormalProof[];
}

export default function FormalMathWorkspacePage() {
  const [projectId, setProjectId] = useState<string>("default-project");
  const [naturalLanguage, setNaturalLanguage] = useState<string>("For all natural numbers n, n + 0 = n");
  const [proofScript, setProofScript] = useState<string>("theorem thm_example (n : Nat) : n + 0 = n := by\n  rfl");
  const [theorems, setTheorems] = useState<FormalTheorem[]>([]);
  const [smtFormula, setSmtFormula] = useState<string>("x > 0 and x < 0");
  const [smtResult, setSmtResult] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    fetchTheorems();
  }, [projectId]);

  const fetchTheorems = async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/formal-math/project/${projectId}`, {
        headers: { Authorization: "Bearer axiom-dev-token" },
      });
      if (res.ok) {
        const data = await res.json();
        setTheorems(data.theorems || []);
      }
    } catch (err) {
      console.error("Failed to load formal theorems:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleFormalize = async () => {
    if (!naturalLanguage.trim()) return;
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/v1/formal-math/formalize", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer axiom-dev-token",
        },
        body: JSON.stringify({
          project_id: projectId,
          natural_language: naturalLanguage,
          language: "LEAN4",
        }),
      });
      if (res.ok) {
        await fetchTheorems();
      }
    } catch (err) {
      console.error("Failed to formalize theorem:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSolveSmt = async () => {
    if (!smtFormula.trim()) return;
    try {
      const res = await fetch("http://localhost:8000/api/v1/formal-math/solve-smt", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer axiom-dev-token",
        },
        body: JSON.stringify({ formula_text: smtFormula }),
      });
      if (res.ok) {
        const data = await res.json();
        setSmtResult(`${data.result}: ${data.diagnostic}`);
      }
    } catch (err) {
      console.error("Failed to solve SMT:", err);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "VERIFIED":
        return "#4ade80";
      case "FORMALIZED":
      case "PROOF_IN_PROGRESS":
        return "#38bdf8";
      case "DISPROVEN":
        return "#f87171";
      default:
        return "#94a3b8";
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif", backgroundColor: "#0f172a", color: "#f8fafc", minHeight: "100vh" }}>
      <header style={{ marginBottom: "2rem", borderBottom: "1px solid #334155", paddingBottom: "1rem" }}>
        <h1 style={{ fontSize: "2rem", fontWeight: "bold", color: "#6366f1" }}>
          Formal Mathematics & Proof Verification Workspace
        </h1>
        <p style={{ color: "#94a3b8", fontSize: "0.95rem" }}>
          AXIOM Phase 16 Lean 4 Theorem Prover, SMT Z3 Solver Gateway, and Proof Artifact Store
        </p>
      </header>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem", marginBottom: "2rem" }}>
        {/* Natural Language Formalizer */}
        <div style={{ padding: "1.5rem", backgroundColor: "#1e293b", borderRadius: "0.5rem", border: "1px solid #334155" }}>
          <h2 style={{ fontSize: "1.1rem", fontWeight: "600", color: "#e2e8f0", marginBottom: "1rem" }}>
            Formalize Natural Language Claim
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
            <textarea
              rows={3}
              placeholder="Enter Natural Language Claim..."
              value={naturalLanguage}
              onChange={(e) => setNaturalLanguage(e.target.value)}
              style={{
                padding: "0.6rem 1rem",
                borderRadius: "0.375rem",
                backgroundColor: "#0f172a",
                border: "1px solid #475569",
                color: "#fff",
              }}
            />
            <button
              onClick={handleFormalize}
              disabled={loading}
              style={{
                alignSelf: "flex-start",
                padding: "0.6rem 1.25rem",
                backgroundColor: "#4f46e5",
                color: "#fff",
                border: "none",
                borderRadius: "0.375rem",
                cursor: "pointer",
                fontWeight: "600",
              }}
            >
              Formalize into Lean 4 Theorem
            </button>
          </div>
        </div>

        {/* SMT Solver Console */}
        <div style={{ padding: "1.5rem", backgroundColor: "#1e293b", borderRadius: "0.5rem", border: "1px solid #334155" }}>
          <h2 style={{ fontSize: "1.1rem", fontWeight: "600", color: "#e2e8f0", marginBottom: "1rem" }}>
            SMT Z3 Logic Solver Console
          </h2>
          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <input
              type="text"
              placeholder="Enter SMT Formula (e.g. x > 0 and x < 0)..."
              value={smtFormula}
              onChange={(e) => setSmtFormula(e.target.value)}
              style={{
                padding: "0.6rem 1rem",
                borderRadius: "0.375rem",
                backgroundColor: "#0f172a",
                border: "1px solid #475569",
                color: "#38bdf8",
                fontFamily: "monospace",
              }}
            />
            <button
              onClick={handleSolveSmt}
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
              Solve SMT Formula
            </button>
            {smtResult && (
              <div style={{ padding: "0.75rem", backgroundColor: "#0f172a", borderRadius: "0.375rem", fontSize: "0.85rem", color: "#a5b4fc" }}>
                {smtResult}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Formal Theorems & Proofs List */}
      <h2 style={{ fontSize: "1.25rem", fontWeight: "600", color: "#cbd5e1", marginBottom: "1rem" }}>
        Formal Theorems ({theorems.length})
      </h2>

      {loading && theorems.length === 0 ? (
        <div style={{ color: "#94a3b8", textAlign: "center", padding: "2rem" }}>Loading formal theorems...</div>
      ) : theorems.length === 0 ? (
        <div style={{ color: "#64748b" }}>No formal theorems in this project yet.</div>
      ) : (
        <div style={{ display: "grid", gap: "1.5rem" }}>
          {theorems.map((thm) => (
            <div key={thm.id} style={{ padding: "1.5rem", backgroundColor: "#1e293b", borderRadius: "0.5rem", border: "1px solid #334155", borderLeft: `5px solid ${getStatusColor(thm.status)}` }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                <span style={{ fontSize: "0.75rem", fontWeight: "bold", padding: "0.2rem 0.6rem", borderRadius: "0.25rem", backgroundColor: "#0f172a", color: getStatusColor(thm.status) }}>
                  {thm.language} • {thm.status}
                </span>
                <span style={{ color: "#94a3b8", fontSize: "0.85rem" }}>{thm.name}</span>
              </div>

              <h3 style={{ fontSize: "1.1rem", fontWeight: "bold", color: "#f8fafc", marginBottom: "0.5rem" }}>
                {thm.natural_language}
              </h3>

              <pre style={{ padding: "0.8rem", backgroundColor: "#0f172a", borderRadius: "0.375rem", fontSize: "0.85rem", color: "#818cf8", overflowX: "auto" }}>
                {thm.formal_statement}
              </pre>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
