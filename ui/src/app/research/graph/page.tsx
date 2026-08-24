"use client";

import React, { useState, useEffect } from "react";

interface GraphEntity {
  id: string;
  name: string;
  entity_type: string;
  domain: string;
  description?: string;
}

interface GraphClaim {
  id: string;
  claim_text: string;
  claim_type: string;
  epistemic_status: string;
  confidence_score: number;
}

interface GraphContradiction {
  id: string;
  claim_a_id: string;
  claim_b_id: string;
  contradiction_type: string;
  reasoning: string;
  resolved: boolean;
}

interface GraphResearchGap {
  id: string;
  gap_type: string;
  description: string;
  severity: string;
}

interface SummaryData {
  project_id: string;
  total_entities: number;
  total_claims: number;
  total_relationships: number;
  total_contradictions: number;
  total_gaps: number;
  entities: GraphEntity[];
  claims: GraphClaim[];
  contradictions: GraphContradiction[];
  research_gaps: GraphResearchGap[];
}

export default function KnowledgeGraphPage() {
  const [projectId, setProjectId] = useState<string>("default-project");
  const [summary, setSummary] = useState<SummaryData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<"entities" | "claims" | "contradictions" | "gaps">("entities");

  useEffect(() => {
    fetchGraphSummary();
  }, [projectId]);

  const fetchGraphSummary = async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/knowledge-graph/summary/${projectId}`, {
        headers: { Authorization: "Bearer axiom-dev-token" },
      });
      if (res.ok) {
        const data = await res.json();
        setSummary(data);
      } else {
        setSummary(null);
      }
    } catch (err) {
      console.error("Failed to load knowledge graph summary:", err);
      setSummary(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif", backgroundColor: "#0f172a", color: "#f8fafc", minHeight: "100vh" }}>
      <header style={{ marginBottom: "2rem", borderBottom: "1px solid #334155", paddingBottom: "1rem" }}>
        <h1 style={{ fontSize: "2rem", fontWeight: "bold", color: "#38bdf8" }}>
          Scientific Knowledge & Claim Graph Workspace
        </h1>
        <p style={{ color: "#94a3b8", fontSize: "0.95rem" }}>
          AXIOM Phase 13 Provenance-Backed Evidence & Claims Representation
        </p>
      </header>

      <div style={{ display: "flex", gap: "1rem", marginBottom: "1.5rem" }}>
        <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", color: "#cbd5e1" }}>
          Project ID:
          <input
            type="text"
            value={projectId}
            onChange={(e) => setProjectId(e.target.value)}
            style={{
              padding: "0.5rem 0.8rem",
              borderRadius: "0.375rem",
              backgroundColor: "#1e293b",
              border: "1px solid #475569",
              color: "#fff",
            }}
          />
        </label>
        <button
          onClick={fetchGraphSummary}
          style={{
            padding: "0.5rem 1rem",
            backgroundColor: "#0284c7",
            color: "#fff",
            border: "none",
            borderRadius: "0.375rem",
            cursor: "pointer",
          }}
        >
          Refresh Graph
        </button>
      </div>

      {/* Summary KPI Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "1rem", marginBottom: "2rem" }}>
        <div style={{ padding: "1rem", backgroundColor: "#1e293b", borderRadius: "0.5rem", border: "1px solid #334155" }}>
          <div style={{ color: "#94a3b8", fontSize: "0.85rem" }}>Entities</div>
          <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#38bdf8" }}>{summary?.total_entities || 0}</div>
        </div>
        <div style={{ padding: "1rem", backgroundColor: "#1e293b", borderRadius: "0.5rem", border: "1px solid #334155" }}>
          <div style={{ color: "#94a3b8", fontSize: "0.85rem" }}>Claims</div>
          <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#818cf8" }}>{summary?.total_claims || 0}</div>
        </div>
        <div style={{ padding: "1rem", backgroundColor: "#1e293b", borderRadius: "0.5rem", border: "1px solid #334155" }}>
          <div style={{ color: "#94a3b8", fontSize: "0.85rem" }}>Contradictions</div>
          <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#f87171" }}>{summary?.total_contradictions || 0}</div>
        </div>
        <div style={{ padding: "1rem", backgroundColor: "#1e293b", borderRadius: "0.5rem", border: "1px solid #334155" }}>
          <div style={{ color: "#94a3b8", fontSize: "0.85rem" }}>Research Gaps</div>
          <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#fbbf24" }}>{summary?.total_gaps || 0}</div>
        </div>
      </div>

      {/* Tab Selectors */}
      <div style={{ display: "flex", gap: "0.5rem", borderBottom: "1px solid #334155", marginBottom: "1.5rem" }}>
        {(["entities", "claims", "contradictions", "gaps"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: "0.75rem 1.25rem",
              backgroundColor: activeTab === tab ? "#0284c7" : "transparent",
              color: activeTab === tab ? "#fff" : "#94a3b8",
              border: "none",
              borderBottom: activeTab === tab ? "2px solid #38bdf8" : "none",
              cursor: "pointer",
              textTransform: "capitalize",
              fontWeight: "600",
            }}
          >
            {tab}
          </button>
        ))}
      </div>

      {loading ? (
        <div style={{ color: "#94a3b8", textAlign: "center", padding: "3rem" }}>Loading Knowledge Graph...</div>
      ) : summary ? (
        <div>
          {activeTab === "entities" && (
            <div style={{ display: "grid", gap: "0.75rem" }}>
              {summary.entities.length === 0 ? (
                <div style={{ color: "#64748b" }}>No entities extracted yet.</div>
              ) : (
                summary.entities.map((e) => (
                  <div key={e.id} style={{ padding: "1rem", backgroundColor: "#1e293b", borderRadius: "0.375rem", borderLeft: "4px solid #38bdf8" }}>
                    <div style={{ fontWeight: "bold", fontSize: "1.05rem" }}>{e.name}</div>
                    <div style={{ color: "#94a3b8", fontSize: "0.85rem", marginTop: "0.25rem" }}>
                      Type: <span style={{ color: "#38bdf8" }}>{e.entity_type}</span> | Domain: {e.domain}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === "claims" && (
            <div style={{ display: "grid", gap: "0.75rem" }}>
              {summary.claims.length === 0 ? (
                <div style={{ color: "#64748b" }}>No claims extracted yet.</div>
              ) : (
                summary.claims.map((c) => (
                  <div key={c.id} style={{ padding: "1rem", backgroundColor: "#1e293b", borderRadius: "0.375rem", borderLeft: "4px solid #818cf8" }}>
                    <div style={{ fontSize: "1rem", color: "#f1f5f9" }}>"{c.claim_text}"</div>
                    <div style={{ color: "#94a3b8", fontSize: "0.85rem", marginTop: "0.4rem" }}>
                      Type: {c.claim_type} | Status: <span style={{ color: c.epistemic_status === "CONTRADICTED" ? "#f87171" : "#4ade80" }}>{c.epistemic_status}</span> | Confidence: {(c.confidence_score * 100).toFixed(0)}%
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === "contradictions" && (
            <div style={{ display: "grid", gap: "0.75rem" }}>
              {summary.contradictions.length === 0 ? (
                <div style={{ color: "#64748b" }}>No contradictions detected in knowledge graph.</div>
              ) : (
                summary.contradictions.map((cd) => (
                  <div key={cd.id} style={{ padding: "1rem", backgroundColor: "#1e293b", borderRadius: "0.375rem", borderLeft: "4px solid #f87171" }}>
                    <div style={{ fontWeight: "bold", color: "#f87171" }}>{cd.contradiction_type} Contradiction</div>
                    <div style={{ color: "#cbd5e1", fontSize: "0.9rem", marginTop: "0.25rem" }}>{cd.reasoning}</div>
                    <div style={{ color: "#94a3b8", fontSize: "0.8rem", marginTop: "0.4rem" }}>
                      Claim A: {cd.claim_a_id.slice(0, 8)} | Claim B: {cd.claim_b_id.slice(0, 8)} | Resolved: {cd.resolved ? "Yes" : "No"}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === "gaps" && (
            <div style={{ display: "grid", gap: "0.75rem" }}>
              {summary.research_gaps.length === 0 ? (
                <div style={{ color: "#64748b" }}>No research gaps identified.</div>
              ) : (
                summary.research_gaps.map((g) => (
                  <div key={g.id} style={{ padding: "1rem", backgroundColor: "#1e293b", borderRadius: "0.375rem", borderLeft: "4px solid #fbbf24" }}>
                    <div style={{ fontWeight: "bold", color: "#fbbf24" }}>{g.gap_type} ({g.severity} Severity)</div>
                    <div style={{ color: "#cbd5e1", fontSize: "0.9rem", marginTop: "0.25rem" }}>{g.description}</div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      ) : (
        <div style={{ color: "#ef4444" }}>Failed to load knowledge graph summary. Check backend connection.</div>
      )}
    </div>
  );
}
