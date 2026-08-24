"use client";

import React, { useState, useEffect } from "react";

interface Challenge {
  id: string;
  version: string;
  title: string;
  domain: string;
  difficulty_level: string;
  statement: string;
}

interface EvaluationRun {
  id: string;
  challenge_id: string;
  outcome: string;
  failure_class: string;
  runtime_sec: number;
  steps_used: number;
  proof_verified: boolean;
  counterexample_found: boolean;
}

export default function BenchmarkDashboardPage() {
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [runs, setRuns] = useState<EvaluationRun[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const resCh = await fetch("http://localhost:8000/api/v1/benchmarks/challenges", {
        headers: { Authorization: "Bearer axiom-dev-token" },
      });
      if (resCh.ok) {
        const dataCh = await resCh.json();
        setChallenges(dataCh.challenges || []);
      }

      const resRuns = await fetch("http://localhost:8000/api/v1/benchmarks/results", {
        headers: { Authorization: "Bearer axiom-dev-token" },
      });
      if (resRuns.ok) {
        const dataRuns = await resRuns.json();
        setRuns(dataRuns.runs || []);
      }
    } catch (err) {
      console.error("Failed to load benchmark data:", err);
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyColor = (level: string) => {
    switch (level) {
      case "LEVEL_0_BASIC":
        return "#4ade80";
      case "LEVEL_1_ELEMENTARY_PROOFS":
        return "#38bdf8";
      case "LEVEL_2_INTERMEDIATE":
        return "#a855f7";
      case "LEVEL_3_ADVANCED":
        return "#f97316";
      default:
        return "#ef4444";
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif", backgroundColor: "#0f172a", color: "#f8fafc", minHeight: "100vh" }}>
      <header style={{ marginBottom: "2rem", borderBottom: "1px solid #334155", paddingBottom: "1rem" }}>
        <h1 style={{ fontSize: "2rem", fontWeight: "bold", color: "#a855f7" }}>
          Mathematical Research Challenge Harness (AXIOM-MATH-001)
        </h1>
        <p style={{ color: "#94a3b8", fontSize: "0.95rem" }}>
          AXIOM Phase 18 Blind Challenge Evaluation, Multi-Axis Scoring, and Anti-Gaming Protection
        </p>
      </header>

      {/* Challenges List */}
      <h2 style={{ fontSize: "1.25rem", fontWeight: "600", color: "#cbd5e1", marginBottom: "1rem" }}>
        Golden Benchmark Challenges ({challenges.length})
      </h2>

      {loading && challenges.length === 0 ? (
        <div style={{ color: "#94a3b8", textAlign: "center", padding: "2rem" }}>Loading benchmark challenges...</div>
      ) : (
        <div style={{ display: "grid", gap: "1.5rem", marginBottom: "2.5rem" }}>
          {challenges.map((ch) => (
            <div key={ch.id} style={{ padding: "1.5rem", backgroundColor: "#1e293b", borderRadius: "0.5rem", border: "1px solid #334155", borderLeft: `5px solid ${getDifficultyColor(ch.difficulty_level)}` }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
                <span style={{ fontSize: "0.75rem", fontWeight: "bold", padding: "0.2rem 0.6rem", borderRadius: "0.25rem", backgroundColor: "#0f172a", color: getDifficultyColor(ch.difficulty_level) }}>
                  {ch.version} • {ch.difficulty_level}
                </span>
                <span style={{ color: "#94a3b8", fontSize: "0.85rem" }}>Domain: {ch.domain}</span>
              </div>
              <h3 style={{ fontSize: "1.1rem", fontWeight: "bold", color: "#f8fafc", marginBottom: "0.5rem" }}>{ch.title}</h3>
              <p style={{ color: "#94a3b8", fontSize: "0.9rem", fontFamily: "monospace", backgroundColor: "#0f172a", padding: "0.75rem", borderRadius: "0.375rem" }}>
                {ch.statement}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Evaluation Runs */}
      <h2 style={{ fontSize: "1.25rem", fontWeight: "600", color: "#cbd5e1", marginBottom: "1rem" }}>
        Evaluation Runs ({runs.length})
      </h2>

      {runs.length === 0 ? (
        <div style={{ color: "#64748b" }}>No evaluation runs executed yet.</div>
      ) : (
        <div style={{ display: "grid", gap: "1rem" }}>
          {runs.map((r) => (
            <div key={r.id} style={{ padding: "1rem 1.5rem", backgroundColor: "#1e293b", borderRadius: "0.5rem", border: "1px solid #334155", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <span style={{ fontWeight: "bold", color: r.outcome === "SOLVED" ? "#4ade80" : "#38bdf8" }}>{r.outcome}</span>
                <span style={{ color: "#94a3b8", fontSize: "0.85rem", marginLeft: "1rem" }}>
                  Runtime: {r.runtime_sec}s • Steps: {r.steps_used}
                </span>
              </div>
              <div style={{ fontSize: "0.85rem", color: "#a5b4fc" }}>
                {r.proof_verified ? "✓ Formal Proof Verified" : r.counterexample_found ? "✓ Counterexample Found" : "In Progress"}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
