"use client";

import React, { useState } from "react";
import Link from "next/link";

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<string>("general");

  return (
    <div style={{ fontFamily: "sans-serif", backgroundColor: "#090d16", color: "#f8fafc", minHeight: "100vh", padding: "2rem" }}>
      <header style={{ marginBottom: "2rem", borderBottom: "1px solid #1e293b", paddingBottom: "1rem" }}>
        <h1 style={{ fontSize: "1.75rem", fontWeight: "bold", color: "#f8fafc" }}>AXIOM System Settings</h1>
        <p style={{ color: "#94a3b8", fontSize: "0.9rem" }}>Manage organization profiles, model routing references, security policies, and integrations</p>
      </header>

      <div style={{ display: "grid", gridTemplateColumns: "220px 1fr", gap: "2rem" }}>
        {/* Navigation Sidebar */}
        <div style={{ padding: "1rem", backgroundColor: "#0f172a", borderRadius: "0.5rem", border: "1px solid #1e293b", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
          {[
            { id: "general", label: "General Profile" },
            { id: "models", label: "Model Routing" },
            { id: "budgets", label: "Budget Policies" },
            { id: "security", label: "Security & Guardrails" },
            { id: "integrations", label: "Formal Engine Integrations" },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              style={{
                padding: "0.6rem 0.8rem",
                borderRadius: "0.375rem",
                border: "none",
                backgroundColor: activeTab === item.id ? "#1e293b" : "transparent",
                color: activeTab === item.id ? "#818cf8" : "#94a3b8",
                fontWeight: activeTab === item.id ? "bold" : "normal",
                textAlign: "left",
                cursor: "pointer",
              }}
            >
              {item.label}
            </button>
          ))}
        </div>

        {/* Tab Panel Content */}
        <div style={{ padding: "1.5rem", backgroundColor: "#0f172a", borderRadius: "0.5rem", border: "1px solid #1e293b" }}>
          {activeTab === "general" && (
            <div>
              <h2 style={{ fontSize: "1.1rem", fontWeight: "bold", marginBottom: "1rem", color: "#e2e8f0" }}>Organization & Profile Settings</h2>
              <div style={{ display: "flex", flexDirection: "column", gap: "1rem", maxWidth: "500px" }}>
                <div>
                  <label style={{ fontSize: "0.85rem", color: "#94a3b8", display: "block", marginBottom: "0.25rem" }}>Organization Name</label>
                  <input type="text" defaultValue="AXIOM Frontier AI Lab" style={{ width: "100%", padding: "0.5rem", backgroundColor: "#1e293b", border: "1px solid #334155", color: "#fff", borderRadius: "0.25rem" }} />
                </div>
                <div>
                  <label style={{ fontSize: "0.85rem", color: "#94a3b8", display: "block", marginBottom: "0.25rem" }}>Default Research Project</label>
                  <input type="text" defaultValue="default-project" style={{ width: "100%", padding: "0.5rem", backgroundColor: "#1e293b", border: "1px solid #334155", color: "#fff", borderRadius: "0.25rem" }} />
                </div>
              </div>
            </div>
          )}

          {activeTab === "models" && (
            <div>
              <h2 style={{ fontSize: "1.1rem", fontWeight: "bold", marginBottom: "1rem", color: "#e2e8f0" }}>Model Router Credentials & Policy</h2>
              <p style={{ color: "#94a3b8", fontSize: "0.85rem", marginBottom: "1rem" }}>
                API keys are stored securely in system environment variables and are isolated from specialist agent runtimes.
              </p>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                <div style={{ padding: "0.75rem", backgroundColor: "#1e293b", borderRadius: "0.375rem", display: "flex", justifyContent: "space-between" }}>
                  <span>OpenAI Provider Reference</span>
                  <span style={{ color: "#4ade80", fontFamily: "monospace" }}>sk-proj-•••••••• (Configured)</span>
                </div>
                <div style={{ padding: "0.75rem", backgroundColor: "#1e293b", borderRadius: "0.375rem", display: "flex", justifyContent: "space-between" }}>
                  <span>Anthropic Provider Reference</span>
                  <span style={{ color: "#4ade80", fontFamily: "monospace" }}>sk-ant-•••••••• (Configured)</span>
                </div>
              </div>
            </div>
          )}

          {activeTab === "budgets" && (
            <div>
              <h2 style={{ fontSize: "1.1rem", fontWeight: "bold", marginBottom: "1rem", color: "#e2e8f0" }}>Global Budget Caps</h2>
              <div style={{ display: "flex", flexDirection: "column", gap: "1rem", maxWidth: "400px" }}>
                <div>
                  <label style={{ fontSize: "0.85rem", color: "#94a3b8" }}>Max Iterations Per Mission</label>
                  <input type="number" defaultValue={20} style={{ width: "100%", padding: "0.5rem", backgroundColor: "#1e293b", border: "1px solid #334155", color: "#fff", borderRadius: "0.25rem", marginTop: "0.25rem" }} />
                </div>
                <div>
                  <label style={{ fontSize: "0.85rem", color: "#94a3b8" }}>Max Runtime Timeout (Seconds)</label>
                  <input type="number" defaultValue={600} style={{ width: "100%", padding: "0.5rem", backgroundColor: "#1e293b", border: "1px solid #334155", color: "#fff", borderRadius: "0.25rem", marginTop: "0.25rem" }} />
                </div>
              </div>
            </div>
          )}

          {activeTab === "security" && (
            <div>
              <h2 style={{ fontSize: "1.1rem", fontWeight: "bold", marginBottom: "1rem", color: "#e2e8f0" }}>Security & Isolation Policy</h2>
              <div style={{ fontSize: "0.85rem", color: "#cbd5e1", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                <div>✓ Multi-tenant RBAC & Project Isolation Enforced</div>
                <div>✓ Tool Allowlist Policy Engine Active</div>
                <div>✓ Subprocess Sandboxing Active (Python AST & Overflow Checks)</div>
                <div>✓ Untrusted External Evidence Redacted for Prompt Injection</div>
              </div>
            </div>
          )}

          {activeTab === "integrations" && (
            <div>
              <h2 style={{ fontSize: "1.1rem", fontWeight: "bold", marginBottom: "1rem", color: "#e2e8f0" }}>Formal & Experimental Systems Status</h2>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                <div style={{ padding: "0.75rem", backgroundColor: "#1e293b", borderRadius: "0.375rem", display: "flex", justifyContent: "space-between" }}>
                  <span>Lean 4 Formal Interactive Prover</span>
                  <span style={{ color: "#4ade80", fontWeight: "bold" }}>● CONNECTED (v4.3)</span>
                </div>
                <div style={{ padding: "0.75rem", backgroundColor: "#1e293b", borderRadius: "0.375rem", display: "flex", justifyContent: "space-between" }}>
                  <span>Z3 SMT Logic Solver Gateway</span>
                  <span style={{ color: "#4ade80", fontWeight: "bold" }}>● CONNECTED (v4.12)</span>
                </div>
                <div style={{ padding: "0.75rem", backgroundColor: "#1e293b", borderRadius: "0.375rem", display: "flex", justifyContent: "space-between" }}>
                  <span>SQLite & Vector Storage</span>
                  <span style={{ color: "#4ade80", fontWeight: "bold" }}>● ACTIVE</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
