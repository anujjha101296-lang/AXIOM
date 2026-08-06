"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import EvidenceGraph from "@/components/demo/EvidenceGraph";
import InteractiveTour from "@/components/demo/InteractiveTour";
import ResearchTimeline from "@/components/demo/ResearchTimeline";
import ResearchTree from "@/components/demo/ResearchTree";
import {
  DemoPhase,
  DemoState,
  PHASE_LABELS,
  PHASE_ORDER,
} from "@/lib/demo-types";
import { API_BASE } from "@/lib/api";
import "./demo.css";

const PHASE_DURATIONS: Record<DemoPhase, number> = {
  intro: 2000,
  question: 2500,
  papers: 4000,
  extracting: 3500,
  graph: 3000,
  notes: 2500,
  contradictions: 2500,
  gaps: 2000,
  hypotheses: 2500,
  experiments: 2500,
  report: 3500,
  complete: 0,
};

function phaseIndex(phase: DemoPhase): number {
  return PHASE_ORDER.indexOf(phase);
}

function phaseAtLeast(current: DemoPhase, target: DemoPhase): boolean {
  return phaseIndex(current) >= phaseIndex(target);
}

export default function GoldenDemoPage() {
  const [state, setState] = useState<DemoState | null>(null);
  const [phase, setPhase] = useState<DemoPhase>("intro");
  const [playing, setPlaying] = useState(false);
  const [tourOpen, setTourOpen] = useState(false);
  const [tourStep, setTourStep] = useState(0);
  const [extractProgress, setExtractProgress] = useState(0);
  const [readingPaper, setReadingPaper] = useState(-1);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const extractRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/demo/state`)
      .then((r) => r.json())
      .then(setState)
      .catch(() => setState(null));
  }, []);

  const clearTimers = useCallback(() => {
    if (timerRef.current) clearTimeout(timerRef.current);
    if (extractRef.current) clearInterval(extractRef.current);
  }, []);

  const advancePhase = useCallback(() => {
    setPhase((p) => {
      const idx = phaseIndex(p);
      if (idx >= PHASE_ORDER.length - 1) {
        setPlaying(false);
        return "complete";
      }
      return PHASE_ORDER[idx + 1];
    });
  }, []);

  useEffect(() => {
    if (!playing || phase === "complete") return;

    if (phase === "extracting") {
      setExtractProgress(0);
      extractRef.current = setInterval(() => {
        setExtractProgress((v) => {
          if (v >= 100) {
            if (extractRef.current) clearInterval(extractRef.current);
            return 100;
          }
          return v + 4;
        });
      }, 120);
    }

    if (phase === "papers") {
      setReadingPaper(0);
      const paperTimer = setInterval(() => {
        setReadingPaper((p) => {
          if (p >= 2) {
            clearInterval(paperTimer);
            return 2;
          }
          return p + 1;
        });
      }, 1200);
      return () => clearInterval(paperTimer);
    }

    timerRef.current = setTimeout(advancePhase, PHASE_DURATIONS[phase]);
    return clearTimers;
  }, [playing, phase, advancePhase, clearTimers]);

  const startDemo = () => {
    clearTimers();
    setPhase("intro");
    setPlaying(true);
    setExtractProgress(0);
    setReadingPaper(-1);
  };

  const resetDemo = () => {
    clearTimers();
    setPlaying(false);
    setPhase("intro");
    setExtractProgress(0);
    setReadingPaper(-1);
  };

  if (!state) {
    return (
      <div className="demo-loading" aria-live="polite">
        <p>Loading Golden Demo…</p>
      </div>
    );
  }

  const progressPct = Math.round((phaseIndex(phase) / (PHASE_ORDER.length - 1)) * 100);
  const timelineActive = Math.min(
    state.timeline.length - 1,
    Math.floor((phaseIndex(phase) / (PHASE_ORDER.length - 1)) * state.timeline.length)
  );

  const treeDepth =
    phase === "complete" ? 4
    : phaseAtLeast(phase, "experiments") ? 4
    : phaseAtLeast(phase, "hypotheses") ? 3
    : phaseAtLeast(phase, "papers") ? 2
    : phaseAtLeast(phase, "question") ? 1
    : 0;

  return (
    <div className="demo-app">
      <header className="demo-hero" data-highlight="hero">
        <div>
          <Link href="/" className="demo-back">← AXIOM Labs</Link>
          <span className="demo-badge-demo">Golden Demo · v0.5</span>
          <h1>{state.project.name}</h1>
          <p className="demo-hero-sub">{state.project.description}</p>
        </div>
        <div className="demo-hero-actions">
          {!playing && phase !== "complete" && (
            <button type="button" className="demo-btn-primary" onClick={startDemo}>
              ▶ Play Demo
            </button>
          )}
          {playing && (
            <button type="button" className="demo-btn-secondary" onClick={() => { clearTimers(); setPlaying(false); }}>
              Pause
            </button>
          )}
          {phase === "complete" && (
            <button type="button" className="demo-btn-primary" onClick={resetDemo}>
              ↺ Replay
            </button>
          )}
          <button type="button" className="demo-btn-secondary" onClick={() => { setTourOpen(true); setTourStep(0); }}>
            Guided Tour
          </button>
          <Link href="/research" className="demo-btn-secondary" style={{ textDecoration: "none", display: "inline-flex", alignItems: "center" }}>
            Open Workspace
          </Link>
        </div>
      </header>

      <div className="demo-progress-strip">
        <div className="demo-progress-label">
          <span>{PHASE_LABELS[phase]}</span>
          <span>{progressPct}%</span>
        </div>
        <div className="demo-progress-track">
          <div className="demo-progress-fill" style={{ width: `${progressPct}%` }} />
        </div>
      </div>

      {phaseAtLeast(phase, "graph") && (
        <div className="demo-stats">
          {[
            ["papers_ingested", "Papers"],
            ["concepts_extracted", "Concepts"],
            ["relationships", "Links"],
            ["hypotheses_generated", "Hypotheses"],
          ].map(([key, label]) => (
            <div key={key} className="demo-stat">
              <div className="demo-stat-value">{state.stats[key] ?? 0}</div>
              <div className="demo-stat-label">{label}</div>
            </div>
          ))}
        </div>
      )}

      <div className="demo-grid">
        <aside className="demo-panel" aria-label="Timeline and tree">
          <h2>Progress</h2>
          <ResearchTimeline events={state.timeline} activeIndex={timelineActive} />
          {phaseAtLeast(phase, "papers") && (
            <>
              <h2 style={{ marginTop: "1.5rem" }}>Research Tree</h2>
              <ResearchTree
                projectName={state.project.name}
                papers={state.papers}
                hypotheses={phaseAtLeast(phase, "hypotheses") ? state.hypotheses : []}
                experiments={phaseAtLeast(phase, "experiments") ? state.experiments : []}
                visibleDepth={treeDepth}
              />
            </>
          )}
        </aside>

        <main className="demo-panel">
          {phase === "complete" && (
            <div className="demo-complete-banner">
              <strong>Research session complete</strong>
              <p style={{ margin: "0.5rem 0 0", color: "#a0a0c0", fontSize: "0.9rem" }}>
                AXIOM ingested {state.stats.papers_ingested} papers, extracted {state.stats.concepts_extracted} concepts,
                and produced a publication-ready report in {state.stats.elapsed_minutes} minutes.
              </p>
            </div>
          )}

          <div
            className={`demo-question-card ${phaseAtLeast(phase, "question") ? "demo-visible" : ""}`}
            data-highlight="question"
          >
            <h2>Research Question</h2>
            <p>{state.project.research_question}</p>
          </div>

          {phaseAtLeast(phase, "papers") && (
            <section className="demo-center-section demo-visible" data-highlight="papers">
              <h2>Papers</h2>
              {state.papers.map((p, i) => (
                <article
                  key={p.id}
                  className={`demo-paper-card demo-visible ${readingPaper === i ? "reading" : ""}`}
                  style={{ animationDelay: `${i * 150}ms` }}
                >
                  <header>
                    <div>
                      <strong>{p.title}</strong>
                      <div className="demo-paper-meta">{p.authors} · {p.year} · {p.pages} pp</div>
                    </div>
                    <span className={`demo-paper-status ${readingPaper === i ? "reading" : ""}`}>
                      {readingPaper < i ? "queued" : readingPaper === i ? "reading…" : "extracted"}
                    </span>
                  </header>
                  {phaseAtLeast(phase, "extracting") && readingPaper >= i && (
                    <p style={{ fontSize: "0.85rem", color: "#a0a0c0", margin: "0.5rem 0 0", lineHeight: 1.5 }}>
                      {p.summary}
                    </p>
                  )}
                </article>
              ))}
            </section>
          )}

          {phase === "extracting" && (
            <div className="demo-center-section demo-visible">
              <h2>Extracting Knowledge…</h2>
              <div className="demo-extract-bar">
                <div className="demo-extract-fill" style={{ width: `${extractProgress}%` }} />
              </div>
              <p style={{ fontSize: "0.85rem", color: "#8888a0" }}>
                Identifying concepts, methods, findings, and relationships across {state.papers.length} papers…
              </p>
            </div>
          )}

          {phaseAtLeast(phase, "graph") && (
            <section className="demo-center-section demo-visible" data-highlight="graph">
              <h2>Evidence Graph</h2>
              <div className="demo-graph-wrap">
                <EvidenceGraph
                  nodes={state.knowledge_nodes}
                  edges={state.knowledge_edges}
                  visible={phaseAtLeast(phase, "graph")}
                />
              </div>
            </section>
          )}

          {phaseAtLeast(phase, "notes") && (
            <section className="demo-center-section demo-visible" data-highlight="notes">
              <h2>Structured Notes</h2>
              {state.notes.map((n, i) => (
                <div key={n.id} className="demo-note-item" style={{ animationDelay: `${i * 100}ms` }}>
                  <strong>{n.title}</strong>
                  <p>{n.body}</p>
                  <div>{n.tags.map((t) => <span key={t} className="demo-tag">{t}</span>)}</div>
                </div>
              ))}
            </section>
          )}

          {phaseAtLeast(phase, "contradictions") && (
            <section className="demo-center-section demo-visible" data-highlight="contradictions">
              <h2>Contradictions Detected</h2>
              {state.contradictions.map((c, i) => (
                <div key={c.id} className="demo-contradiction" style={{ animationDelay: `${i * 150}ms` }}>
                  <div className="claims">
                    <div><small>{c.source_a}</small><br />{c.claim_a}</div>
                    <span className="vs">VS</span>
                    <div><small>{c.source_b}</small><br />{c.claim_b}</div>
                  </div>
                  <div className="resolution">↳ {c.resolution}</div>
                </div>
              ))}
            </section>
          )}

          {phaseAtLeast(phase, "gaps") && (
            <section className="demo-center-section demo-visible" data-highlight="gaps">
              <h2>Research Gaps</h2>
              {state.gaps.map((g, i) => (
                <div key={g.id} className="demo-gap-item" style={{ animationDelay: `${i * 100}ms` }}>
                  <span className={`demo-gap-priority ${g.priority}`}>{g.priority}</span>
                  <div>
                    <strong>{g.area}</strong>
                    <p style={{ margin: "0.25rem 0 0", fontSize: "0.8rem", color: "#a0a0c0" }}>{g.description}</p>
                  </div>
                </div>
              ))}
            </section>
          )}

          {phaseAtLeast(phase, "hypotheses") && (
            <section className="demo-center-section demo-visible" data-highlight="hypotheses">
              <h2>Hypotheses</h2>
              {state.hypotheses.map((h, i) => (
                <div key={h.id} className="demo-hyp-card" style={{ animationDelay: `${i * 120}ms` }}>
                  <span className="demo-hyp-confidence">{Math.round(h.confidence * 100)}% confidence</span>
                  <p style={{ margin: "0 0 0.5rem", fontSize: "0.9rem", lineHeight: 1.5 }}>{h.statement}</p>
                  <p style={{ margin: 0, fontSize: "0.8rem", color: "#8888a0" }}>{h.rationale}</p>
                </div>
              ))}
            </section>
          )}

          {phaseAtLeast(phase, "experiments") && (
            <section className="demo-center-section demo-visible" data-highlight="experiments">
              <h2>Experiment Plan</h2>
              {state.experiments.map((e, i) => (
                <div key={e.id} className="demo-exp-card" style={{ animationDelay: `${i * 120}ms` }}>
                  <strong>{e.title}</strong>
                  <p style={{ fontSize: "0.85rem", margin: "0.5rem 0", color: "#a0a0c0" }}>{e.objective}</p>
                  <p style={{ fontSize: "0.8rem", margin: 0 }}><strong>Method:</strong> {e.method}</p>
                  <p style={{ fontSize: "0.8rem", margin: "0.35rem 0 0", color: "#10b981" }}>
                    Expected: {e.expected_outcome}
                  </p>
                </div>
              ))}
            </section>
          )}

          {phaseAtLeast(phase, "report") && (
            <section className={`demo-report ${phaseAtLeast(phase, "report") ? "demo-visible" : ""}`} data-highlight="report">
              <h3>{state.report.title}</h3>
              <p className="abstract">{state.report.abstract}</p>
              {state.report.sections.map((s) => (
                <section key={s.heading}>
                  <h4>{s.heading}</h4>
                  <p>{s.content}</p>
                </section>
              ))}
            </section>
          )}
        </main>

        <aside className="demo-panel" aria-label="Live insights">
          <h2>Live Insights</h2>
          {phase === "intro" && (
            <p style={{ color: "#8888a0", fontSize: "0.9rem", lineHeight: 1.6 }}>
              Press <strong>Play Demo</strong> to watch AXIOM transform a new research topic into a complete
              research program — no manual setup required.
            </p>
          )}
          {phaseAtLeast(phase, "question") && (
            <div style={{ marginBottom: "1rem" }}>
              <p style={{ fontSize: "0.8rem", color: "#5a5a80", marginBottom: "0.5rem" }}>ACTIVE PROJECT</p>
              <p style={{ fontSize: "0.9rem", lineHeight: 1.5 }}>{state.project.description}</p>
            </div>
          )}
          {phaseAtLeast(phase, "graph") && (
            <div style={{ marginBottom: "1rem" }}>
              <p style={{ fontSize: "0.8rem", color: "#5a5a80" }}>KNOWLEDGE NODES</p>
              <ul style={{ listStyle: "none", padding: 0, margin: "0.5rem 0 0" }}>
                {state.knowledge_nodes.slice(0, 5).map((n) => (
                  <li key={n.id} style={{ fontSize: "0.8rem", padding: "0.25rem 0", color: "#c8c8d8" }}>
                    <span style={{ color: n.node_type === "contradiction" ? "#f43f5e" : "#818cf8" }}>●</span> {n.label}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {phaseAtLeast(phase, "hypotheses") && (
            <div>
              <p style={{ fontSize: "0.8rem", color: "#5a5a80" }}>TOP HYPOTHESIS</p>
              <p style={{ fontSize: "0.85rem", lineHeight: 1.5, marginTop: "0.5rem" }}>
                {state.hypotheses[0]?.statement}
              </p>
            </div>
          )}
          {phase === "complete" && (
            <div style={{ marginTop: "1rem", padding: "1rem", background: "rgba(99,102,241,0.08)", borderRadius: "12px" }}>
              <p style={{ fontSize: "0.85rem", lineHeight: 1.6, margin: 0 }}>
                Ready for researchers, investors, and lab pilots. All outputs are evidence-classified with explicit limitations.
              </p>
            </div>
          )}
        </aside>
      </div>

      {tourOpen && (
        <InteractiveTour
          steps={state.tour_steps}
          current={tourStep}
          onNext={() => setTourStep((s) => Math.min(s + 1, state.tour_steps.length - 1))}
          onPrev={() => setTourStep((s) => Math.max(s - 1, 0))}
          onClose={() => setTourOpen(false)}
          onJump={setTourStep}
        />
      )}
    </div>
  );
}
