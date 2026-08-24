"use client";

import Link from "next/link";
import React, { useState } from "react";

export default function AxiomLandingPage() {
  const [activeTab, setActiveTab] = useState<string>("mission");

  return (
    <div style={{ fontFamily: "sans-serif", backgroundColor: "#090d16", color: "#f8fafc", minHeight: "100vh" }}>
      {/* Brand Differentiation Banner */}
      <div style={{ backgroundColor: "#1e1b4b", color: "#c7d2fe", padding: "0.5rem 1rem", fontSize: "0.85rem", textAlign: "center", borderBottom: "1px solid #3730a3" }}>
        <strong>AXIOM Research OS</strong> — An autonomous AI system for scientific research, computational experimentation, and formal proof verification.
      </div>

      {/* Navigation */}
      <nav style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "1.25rem 2rem", borderBottom: "1px solid #1e293b", maxWidth: "1200px", margin: "0 auto" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <span style={{ fontSize: "1.5rem", fontWeight: "bold", background: "linear-gradient(to right, #6366f1, #a855f7, #ec4899)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
            AXIOM
          </span>
          <span style={{ fontSize: "0.75rem", padding: "0.2rem 0.5rem", borderRadius: "0.25rem", backgroundColor: "#1e293b", color: "#94a3b8" }}>
            v0.1.0-rc1
          </span>
        </div>

        <div style={{ display: "flex", gap: "1.5rem", fontSize: "0.9rem", color: "#cbd5e1" }}>
          <Link href="/workspace" style={{ color: "inherit", textDecoration: "none" }}>Workspace</Link>
          <Link href="/research/mission-control" style={{ color: "inherit", textDecoration: "none" }}>Mission Control</Link>
          <Link href="/research/formal" style={{ color: "inherit", textDecoration: "none" }}>Formal Math</Link>
          <Link href="/research/benchmarks" style={{ color: "inherit", textDecoration: "none" }}>Benchmarks</Link>
          <Link href="/research/control-plane" style={{ color: "inherit", textDecoration: "none" }}>Control Plane</Link>
        </div>

        <Link href="/workspace" style={{ padding: "0.5rem 1.25rem", backgroundColor: "#6366f1", color: "#fff", borderRadius: "0.375rem", textDecoration: "none", fontWeight: "600", fontSize: "0.9rem" }}>
          Start Research
        </Link>
      </nav>

      {/* Hero Section */}
      <section style={{ textAlign: "center", padding: "4rem 1.5rem 3rem", maxWidth: "900px", margin: "0 auto" }}>
        <h1 style={{ fontSize: "3rem", fontWeight: "800", lineHeight: "1.2", marginBottom: "1.25rem", background: "linear-gradient(to right, #ffffff, #cbd5e1)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
          An autonomous research system for discovering, testing, and verifying new knowledge.
        </h1>
        <p style={{ fontSize: "1.2rem", color: "#94a3b8", lineHeight: "1.6", marginBottom: "2rem" }}>
          AXIOM combines AI agents, scientific literature, computational experiments, knowledge graphs, and formal verification into one unified research environment.
        </p>

        <div style={{ display: "flex", justifyContent: "center", gap: "1rem", marginBottom: "3rem" }}>
          <Link href="/workspace" style={{ padding: "0.75rem 1.75rem", backgroundColor: "#6366f1", color: "#fff", borderRadius: "0.375rem", textDecoration: "none", fontWeight: "600", fontSize: "1rem" }}>
            Start Research
          </Link>
          <a href="#product-showcase" style={{ padding: "0.75rem 1.75rem", backgroundColor: "#1e293b", color: "#e2e8f0", borderRadius: "0.375rem", textDecoration: "none", fontWeight: "600", fontSize: "1rem", border: "1px solid #334155" }}>
            View Demo
          </a>
        </div>
      </section>

      {/* Section 2: Centerpiece Interactive Product Showcase */}
      <section id="product-showcase" style={{ maxWidth: "1100px", margin: "0 auto 5rem", padding: "0 1.5rem" }}>
        <div style={{ backgroundColor: "#0f172a", border: "1px solid #334155", borderRadius: "0.75rem", overflow: "hidden", boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.5)" }}>
          {/* Header */}
          <div style={{ backgroundColor: "#1e293b", padding: "0.75rem 1.25rem", borderBottom: "1px solid #334155", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span style={{ width: "12px", height: "12px", borderRadius: "50%", backgroundColor: "#ef4444" }}></span>
              <span style={{ width: "12px", height: "12px", borderRadius: "50%", backgroundColor: "#eab308" }}></span>
              <span style={{ width: "12px", height: "12px", borderRadius: "50%", backgroundColor: "#22c55e" }}></span>
              <span style={{ marginLeft: "1rem", fontFamily: "monospace", fontSize: "0.85rem", color: "#94a3b8" }}>AXIOM Research OS — Mission Workspace</span>
            </div>
            <span style={{ fontSize: "0.75rem", padding: "0.2rem 0.6rem", borderRadius: "0.25rem", backgroundColor: "#065f46", color: "#34d399", fontWeight: "bold" }}>
              ● ACTIVE MISSION
            </span>
          </div>

          {/* Body */}
          <div style={{ display: "grid", gridTemplateColumns: "240px 1fr", minHeight: "450px" }}>
            {/* Sidebar */}
            <div style={{ borderRight: "1px solid #1e293b", padding: "1.25rem", backgroundColor: "#0b1329" }}>
              <div style={{ fontSize: "0.75rem", fontWeight: "bold", color: "#64748b", textTransform: "uppercase", marginBottom: "0.75rem" }}>Navigation</div>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", fontSize: "0.9rem" }}>
                <div style={{ padding: "0.5rem", borderRadius: "0.25rem", backgroundColor: "#1e293b", color: "#818cf8", fontWeight: "bold" }}>🎯 Missions</div>
                <Link href="/research/graph" style={{ padding: "0.5rem", color: "#94a3b8", textDecoration: "none" }}>🕸 Knowledge Graph</Link>
                <Link href="/research/hypotheses" style={{ padding: "0.5rem", color: "#94a3b8", textDecoration: "none" }}>💡 Hypotheses</Link>
                <Link href="/research/experiments" style={{ padding: "0.5rem", color: "#94a3b8", textDecoration: "none" }}>⚗ Experiments</Link>
                <Link href="/research/formal" style={{ padding: "0.5rem", color: "#94a3b8", textDecoration: "none" }}>∴ Proofs</Link>
                <Link href="/research/benchmarks" style={{ padding: "0.5rem", color: "#94a3b8", textDecoration: "none" }}>📊 Benchmarks</Link>
              </div>
            </div>

            {/* Main Content */}
            <div style={{ padding: "1.5rem", backgroundColor: "#0f172a" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1.5rem" }}>
                <div>
                  <h3 style={{ fontSize: "1.25rem", fontWeight: "bold", color: "#f8fafc", marginBottom: "0.25rem" }}>Riemann Hypothesis & Zero Distribution Bounds</h3>
                  <p style={{ color: "#94a3b8", fontSize: "0.85rem" }}>Objective: Evaluate non-trivial zero bounds and verify finite domain counterexamples.</p>
                </div>
                <span style={{ fontSize: "0.8rem", color: "#a7f3d0", backgroundColor: "#064e3b", padding: "0.3rem 0.75rem", borderRadius: "0.375rem" }}>
                  Progress: 82%
                </span>
              </div>

              {/* Research Tracks */}
              <div style={{ marginBottom: "1.5rem" }}>
                <div style={{ fontSize: "0.8rem", fontWeight: "bold", color: "#64748b", textTransform: "uppercase", marginBottom: "0.75rem" }}>Active Research Tracks</div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
                  <div style={{ padding: "0.75rem", backgroundColor: "#1e293b", borderRadius: "0.375rem", border: "1px solid #334155", display: "flex", justifyContent: "space-between", fontSize: "0.85rem" }}>
                    <span>● Literature Research</span>
                    <span style={{ color: "#38bdf8", fontWeight: "bold" }}>RUNNING</span>
                  </div>
                  <div style={{ padding: "0.75rem", backgroundColor: "#1e293b", borderRadius: "0.375rem", border: "1px solid #334155", display: "flex", justifyContent: "space-between", fontSize: "0.85rem" }}>
                    <span>● Counterexample Search</span>
                    <span style={{ color: "#38bdf8", fontWeight: "bold" }}>RUNNING</span>
                  </div>
                  <div style={{ padding: "0.75rem", backgroundColor: "#1e293b", borderRadius: "0.375rem", border: "1px solid #334155", display: "flex", justifyContent: "space-between", fontSize: "0.85rem" }}>
                    <span>● Formalization</span>
                    <span style={{ color: "#eab308", fontWeight: "bold" }}>WAITING</span>
                  </div>
                  <div style={{ padding: "0.75rem", backgroundColor: "#1e293b", borderRadius: "0.375rem", border: "1px solid #334155", display: "flex", justifyContent: "space-between", fontSize: "0.85rem" }}>
                    <span>● Computational Experiment</span>
                    <span style={{ color: "#4ade80", fontWeight: "bold" }}>COMPLETE</span>
                  </div>
                </div>
              </div>

              {/* Evidence Metrics */}
              <div style={{ padding: "1rem", backgroundColor: "#182238", borderRadius: "0.5rem", border: "1px solid #2e3d60", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <div style={{ fontSize: "0.9rem", fontWeight: "bold", color: "#e2e8f0" }}>Evidence Matrix</div>
                  <div style={{ fontSize: "0.85rem", color: "#94a3b8" }}>42 sources · 17 claims · 6 hypotheses · 8 verified lemmas</div>
                </div>
                <div style={{ display: "flex", gap: "0.5rem" }}>
                  <Link href="/research/graph" style={{ padding: "0.4rem 0.8rem", backgroundColor: "#312e81", color: "#c7d2fe", borderRadius: "0.25rem", textDecoration: "none", fontSize: "0.8rem" }}>
                    Open Graph
                  </Link>
                  <Link href="/research/mission-control" style={{ padding: "0.4rem 0.8rem", backgroundColor: "#4338ca", color: "#fff", borderRadius: "0.25rem", textDecoration: "none", fontSize: "0.8rem" }}>
                    View Mission
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Section 3: "How AXIOM Researches" Visual Core Loop */}
      <section style={{ maxWidth: "1100px", margin: "0 auto 5rem", padding: "0 1.5rem" }}>
        <h2 style={{ textAlign: "center", fontSize: "2rem", fontWeight: "bold", marginBottom: "0.5rem", color: "#f8fafc" }}>
          How AXIOM Researches
        </h2>
        <p style={{ textAlign: "center", color: "#94a3b8", marginBottom: "3rem" }}>
          The autonomous scientific cycle: from natural question to machine-checked proof.
        </p>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "1rem" }}>
          {[
            { step: "01", title: "ASK", desc: "Define objective & boundary conditions" },
            { step: "02", title: "RESEARCH", desc: "Retrieve literature & extract claims" },
            { step: "03", title: "UNDERSTAND", desc: "Construct knowledge graph edges" },
            { step: "04", title: "HYPOTHESIZE", desc: "Formulate testable conjectures" },
            { step: "05", title: "EXPERIMENT", desc: "Run sandboxed computations" },
            { step: "06", title: "CHALLENGE", desc: "Search finite counterexamples" },
            { step: "07", title: "FORMALIZE", desc: "Translate to Lean 4 & SMT Z3" },
            { step: "08", title: "VERIFY", desc: "Kernel-checked proof checking" },
            { step: "09", title: "LEARN ↺", desc: "Persist approach memory" },
          ].map((item) => (
            <div key={item.step} style={{ padding: "1.25rem", backgroundColor: "#0f172a", borderRadius: "0.5rem", border: "1px solid #1e293b", textAlign: "center" }}>
              <div style={{ fontSize: "0.75rem", fontWeight: "bold", color: "#6366f1", marginBottom: "0.25rem" }}>STEP {item.step}</div>
              <div style={{ fontSize: "1.1rem", fontWeight: "bold", color: "#f8fafc", marginBottom: "0.5rem" }}>{item.title}</div>
              <div style={{ fontSize: "0.8rem", color: "#94a3b8" }}>{item.desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Section 4: Specialist Multi-Agent Research Team */}
      <section style={{ maxWidth: "1100px", margin: "0 auto 5rem", padding: "0 1.5rem" }}>
        <h2 style={{ textAlign: "center", fontSize: "2rem", fontWeight: "bold", marginBottom: "0.5rem", color: "#f8fafc" }}>
          Specialist Multi-Agent Team
        </h2>
        <p style={{ textAlign: "center", color: "#94a3b8", marginBottom: "3rem" }}>
          Bounded roles with strict tool permissions, step limits, and budget policy enforcement.
        </p>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "1.25rem" }}>
          {[
            { icon: "🔎", role: "Literature Researcher", desc: "Semantic arXiv ingestion & claim extraction" },
            { icon: "∑", role: "Mathematician", desc: "Lemma formulation & strategy planning" },
            { icon: "∴", role: "Formalizer", desc: "Natural language to Lean 4 / SMT Z3 translation" },
            { icon: "⚗", role: "Experimentalist", desc: "Sandboxed Python numerical simulations" },
            { icon: "⚠", role: "Counterexample Hunter", desc: "Bounded domain refutation sweeps" },
            { icon: "✓", role: "Proof Verifier", desc: "Kernel-level Lean 4 proof verification" },
            { icon: "◈", role: "Research Critic", desc: "Audits research progress & recommends pivots" },
          ].map((ag) => (
            <div key={ag.role} style={{ padding: "1.25rem", backgroundColor: "#0f172a", borderRadius: "0.5rem", border: "1px solid #1e293b", display: "flex", gap: "1rem", alignItems: "center" }}>
              <span style={{ fontSize: "2rem" }}>{ag.icon}</span>
              <div>
                <div style={{ fontWeight: "bold", color: "#f8fafc", fontSize: "1rem" }}>{ag.role}</div>
                <div style={{ fontSize: "0.85rem", color: "#94a3b8" }}>{ag.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Section 7 & 8: Evidence vs Proof Distinction */}
      <section style={{ maxWidth: "1100px", margin: "0 auto 5rem", padding: "0 1.5rem" }}>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem" }}>
          {/* Card 1: Computational Experiments */}
          <div style={{ padding: "1.5rem", backgroundColor: "#0f172a", borderRadius: "0.5rem", border: "1px solid #334155" }}>
            <h3 style={{ fontSize: "1.2rem", fontWeight: "bold", color: "#38bdf8", marginBottom: "1rem" }}>
              ⚗ Computational Experiments
            </h3>
            <div style={{ fontFamily: "monospace", fontSize: "0.85rem", color: "#cbd5e1", backgroundColor: "#070b14", padding: "1rem", borderRadius: "0.375rem", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              <div>Experiment #184</div>
              <div>Hypothesis: H(n) holds for all n</div>
              <div>Domain: n = 1 ... 10,000,000</div>
              <div style={{ color: "#4ade80" }}>Result: 10,000,000 / 10,000,000 passed</div>
              <div style={{ color: "#4ade80" }}>Independent verification: PASSED</div>
              <div>Scientific interpretation: SUPPORTED IN TESTED DOMAIN</div>
              <div style={{ color: "#f43f5e", fontWeight: "bold" }}>Formal proof: NOT ESTABLISHED</div>
            </div>
          </div>

          {/* Card 2: Formal Proof Verification */}
          <div style={{ padding: "1.5rem", backgroundColor: "#0f172a", borderRadius: "0.5rem", border: "1px solid #334155" }}>
            <h3 style={{ fontSize: "1.2rem", fontWeight: "bold", color: "#a855f7", marginBottom: "1rem" }}>
              ∴ Formal Proof Verification
            </h3>
            <div style={{ fontFamily: "monospace", fontSize: "0.85rem", color: "#cbd5e1", backgroundColor: "#070b14", padding: "1rem", borderRadius: "0.375rem", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              <div>Natural Language Claim</div>
              <div>↓</div>
              <div>Lean 4 Formal Statement</div>
              <div>↓</div>
              <div>Proof Tactic Candidate</div>
              <div>↓</div>
              <div>Lean 4 Kernel Check</div>
              <div style={{ color: "#4ade80", fontWeight: "bold" }}>✓ VERIFIED PROOF (Sorry-Free)</div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ textAlign: "center", padding: "3rem 1.5rem", borderTop: "1px solid #1e293b", color: "#64748b", fontSize: "0.85rem" }}>
        AXIOM Research Operating System v0.1.0-rc1 • Built by DeepMind Agentic Team
      </footer>
    </div>
  );
}
