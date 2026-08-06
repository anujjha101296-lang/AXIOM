"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import React, { useCallback, useEffect, useState } from "react";
import {
  API_BASE,
  authHeaders,
  clearAuth,
  getStoredToken,
  parseApiError,
} from "@/lib/api";

interface RunSummary {
  id: string;
  research_question: string;
  status: string;
  benchmark_id?: string;
  created_at: string;
}

interface ResearchState {
  run_id: string;
  research_question: string;
  current_phase: string;
  current_iteration: number;
  max_iterations: number;
  subproblems: string[];
  hypotheses: Array<{
    id: string;
    statement: string;
    score: number;
    rank: number;
    rejected: boolean;
    status: string;
  }>;
  evidence: Array<{ source: string; content: string; claim_status: string }>;
  claims: Array<{ statement: string; status: string; confidence: number }>;
  failed_attempts: Array<{ approach: string; failure_reason: string; learned: string }>;
  experiments: Array<{ description: string; success: boolean; result: string }>;
  timeline: Array<{ phase: string; detail: string; worker: string; iteration: number }>;
  active_workers: string[];
  final_report: string;
  confidence: number;
  open_questions: string[];
  uncertainties: string[];
}

interface Benchmark {
  id: string;
  title: string;
  problem_statement: string;
  domain: string;
}

export default function ResearchRunsPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [state, setState] = useState<ResearchState | null>(null);
  const [benchmarks, setBenchmarks] = useState<Benchmark[]>([]);
  const [question, setQuestion] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [pollId, setPollId] = useState<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    const t = getStoredToken();
    if (!t) {
      router.replace("/login");
      return;
    }
    setToken(t);
  }, [router]);

  const apiFetch = useCallback(
    async (path: string, init?: RequestInit) => {
      if (!token) throw new Error("Not authenticated");
      const res = await fetch(`${API_BASE}${path}`, {
        ...init,
        headers: { ...authHeaders(token), ...(init?.headers || {}) },
      });
      if (res.status === 401) {
        clearAuth();
        router.replace("/login");
        throw new Error("Session expired");
      }
      return res;
    },
    [token, router]
  );

  const loadRuns = useCallback(async () => {
    if (!token) return;
    try {
      const res = await apiFetch("/research-loop/runs");
      if (res.ok) setRuns(await res.json());
    } catch (e) {
      setStatus(String(e));
    }
  }, [token, apiFetch]);

  const loadBenchmarks = useCallback(async () => {
    if (!token) return;
    try {
      const res = await apiFetch("/research-loop/benchmarks");
      if (res.ok) setBenchmarks(await res.json());
    } catch {
      /* ignore */
    }
  }, [token, apiFetch]);

  const loadRun = useCallback(
    async (runId: string) => {
      if (!token) return;
      setLoading(true);
      try {
        const res = await apiFetch(`/research-loop/runs/${runId}`);
        if (!res.ok) throw new Error(await parseApiError(res));
        const data = await res.json();
        setState(data.state);
        setSelectedId(runId);
      } catch (e) {
        setStatus(String(e));
      } finally {
        setLoading(false);
      }
    },
    [token, apiFetch]
  );

  useEffect(() => {
    if (token) {
      loadRuns();
      loadBenchmarks();
    }
  }, [token, loadRuns, loadBenchmarks]);

  useEffect(() => {
    if (pollId) clearInterval(pollId);
    if (selectedId && state && !state.final_report) {
      const id = setInterval(() => loadRun(selectedId), 3000);
      setPollId(id);
      return () => clearInterval(id);
    }
    return undefined;
  }, [selectedId, state?.final_report, loadRun]);

  const createRun = async () => {
    if (!question.trim()) return;
    setLoading(true);
    try {
      const res = await apiFetch("/research-loop/runs", {
        method: "POST",
        body: JSON.stringify({ research_question: question, max_iterations: 5 }),
      });
      if (!res.ok) throw new Error(await parseApiError(res));
      const data = await res.json();
      await apiFetch(`/research-loop/runs/${data.run_id}/start`, { method: "POST" });
      setQuestion("");
      await loadRuns();
      await loadRun(data.run_id);
      setStatus("Research run started");
    } catch (e) {
      setStatus(String(e));
    } finally {
      setLoading(false);
    }
  };

  const runBenchmark = async (benchmarkId: string) => {
    setLoading(true);
    try {
      const res = await apiFetch("/research-loop/benchmarks/run", {
        method: "POST",
        body: JSON.stringify({ benchmark_id: benchmarkId, max_iterations: 5 }),
      });
      if (!res.ok) throw new Error(await parseApiError(res));
      const data = await res.json();
      await loadRuns();
      await loadRun(data.run_id);
      setStatus(`Benchmark run started: ${benchmarkId}`);
    } catch (e) {
      setStatus(String(e));
    } finally {
      setLoading(false);
    }
  };

  const controlRun = async (action: "pause" | "resume" | "cancel") => {
    if (!selectedId) return;
    try {
      await apiFetch(`/research-loop/runs/${selectedId}/${action}`, { method: "POST" });
      setStatus(`${action} requested`);
      await loadRun(selectedId);
    } catch (e) {
      setStatus(String(e));
    }
  };

  if (!token) return <div className="runs-loading">Loading…</div>;

  return (
    <div className="runs-app">
      <header className="runs-header">
        <div>
          <Link href="/research" className="runs-back">← Research Workspace</Link>
          <h1>Autonomous Research Runs</h1>
          <p>Closed-loop research with evidence tracking and failure memory</p>
        </div>
      </header>

      {status && <div className="runs-status" role="status">{status}</div>}

      <div className="runs-grid">
        <aside className="runs-sidebar">
          <h2>New Run</h2>
          <textarea
            placeholder="Enter a bounded research question…"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            rows={3}
            aria-label="Research question"
          />
          <button type="button" onClick={createRun} disabled={loading || !question.trim()}>
            Start Run
          </button>

          <h2>Benchmarks</h2>
          <ul className="runs-benchmarks">
            {benchmarks.map((b) => (
              <li key={b.id}>
                <button type="button" onClick={() => runBenchmark(b.id)} disabled={loading}>
                  {b.title}
                </button>
                <small>{b.domain}</small>
              </li>
            ))}
          </ul>

          <h2>Runs</h2>
          <ul className="runs-list">
            {runs.map((r) => (
              <li key={r.id}>
                <button
                  type="button"
                  className={selectedId === r.id ? "active" : ""}
                  onClick={() => loadRun(r.id)}
                >
                  <strong>{r.research_question.slice(0, 50)}…</strong>
                  <span>{r.status}</span>
                </button>
              </li>
            ))}
          </ul>
        </aside>

        <main className="runs-main">
          {!state ? (
            <p className="runs-empty">Select or start a research run to inspect the loop.</p>
          ) : (
            <>
              <section className="runs-overview">
                <h2>Objective</h2>
                <p>{state.research_question}</p>
                <div className="runs-meta">
                  <span>Phase: <strong>{state.current_phase}</strong></span>
                  <span>Iteration: {state.current_iteration}/{state.max_iterations}</span>
                  <span>Confidence: {(state.confidence * 100).toFixed(0)}%</span>
                  {state.active_workers.length > 0 && (
                    <span>Active: {state.active_workers.join(", ")}</span>
                  )}
                </div>
                <div className="runs-controls">
                  <button type="button" onClick={() => controlRun("pause")}>Pause</button>
                  <button type="button" onClick={() => controlRun("resume")}>Resume</button>
                  <button type="button" onClick={() => controlRun("cancel")}>Terminate</button>
                </div>
              </section>

              <section>
                <h3>Research Tree</h3>
                <div className="runs-tree">
                  <div className="runs-tree-node">📋 {state.subproblems.length} subproblems</div>
                  <div className="runs-tree-node">📚 {state.evidence.length} evidence items</div>
                  <div className="runs-tree-node">💡 {state.hypotheses.length} hypotheses</div>
                  <div className="runs-tree-node">🧪 {state.experiments.length} experiments</div>
                  <div className="runs-tree-node">❌ {state.failed_attempts.length} failed attempts</div>
                  <div className="runs-tree-node">✓ {state.claims.filter((c) => c.status === "SUPPORTED").length} supported claims</div>
                </div>
              </section>

              <section>
                <h3>Hypotheses</h3>
                {state.hypotheses.map((h) => (
                  <div key={h.id} className={`runs-hyp ${h.rejected ? "rejected" : ""}`}>
                    <span className="runs-badge">{h.status}</span>
                    <strong>#{h.rank}</strong> {h.statement}
                    <small>score={h.score.toFixed(2)}</small>
                  </div>
                ))}
              </section>

              <section>
                <h3>Failures</h3>
                {state.failed_attempts.length === 0 ? (
                  <p className="runs-muted">No failed attempts recorded.</p>
                ) : (
                  state.failed_attempts.map((f, i) => (
                    <div key={i} className="runs-failure">
                      <strong>{f.approach}</strong>
                      <p>{f.failure_reason}</p>
                      {f.learned && <small>Learned: {f.learned}</small>}
                    </div>
                  ))
                )}
              </section>

              <section>
                <h3>Timeline</h3>
                <ul className="runs-timeline">
                  {state.timeline.slice(-15).map((t, i) => (
                    <li key={i}>
                      <span className="runs-phase">{t.phase}</span>
                      <span>{t.detail}</span>
                      <small>iter {t.iteration} · {t.worker}</small>
                    </li>
                  ))}
                </ul>
              </section>

              {state.final_report && (
                <section>
                  <h3>Final Report</h3>
                  <pre className="runs-report">{state.final_report}</pre>
                </section>
              )}
            </>
          )}
        </main>
      </div>

      <style jsx>{`
        .runs-app { min-height: 100vh; background: #0a0a0f; color: #e8e8ef; font-family: Inter, system-ui, sans-serif; }
        .runs-loading { padding: 4rem; text-align: center; color: #888; }
        .runs-header { padding: 1.5rem 2rem; border-bottom: 1px solid #1e1e2e; }
        .runs-back { color: #7c8cff; text-decoration: none; font-size: 0.85rem; }
        .runs-header h1 { margin: 0.5rem 0 0.25rem; }
        .runs-header p { margin: 0; color: #8888a0; font-size: 0.9rem; }
        .runs-status { margin: 1rem 2rem; padding: 0.75rem; background: #12121a; border-radius: 8px; }
        .runs-grid { display: grid; grid-template-columns: 300px 1fr; min-height: calc(100vh - 120px); }
        .runs-sidebar { border-right: 1px solid #1e1e2e; padding: 1.5rem; }
        .runs-sidebar h2 { font-size: 0.8rem; text-transform: uppercase; color: #8888a0; margin: 1.5rem 0 0.75rem; }
        .runs-sidebar textarea, .runs-sidebar input { width: 100%; box-sizing: border-box; background: #12121a; border: 1px solid #2a2a3a; color: #e8e8ef; padding: 0.5rem; border-radius: 6px; margin-bottom: 0.5rem; }
        .runs-sidebar button { background: #4f5dff; color: white; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; width: 100%; margin-bottom: 0.5rem; }
        .runs-list, .runs-benchmarks { list-style: none; padding: 0; }
        .runs-list button, .runs-benchmarks button { width: 100%; text-align: left; background: transparent; border: 1px solid transparent; color: #e8e8ef; padding: 0.6rem; border-radius: 6px; cursor: pointer; }
        .runs-list button.active, .runs-list button:hover { background: #12121a; border-color: #2a2a3a; }
        .runs-list span, .runs-benchmarks small { display: block; font-size: 0.75rem; color: #8888a0; }
        .runs-main { padding: 1.5rem 2rem; overflow-y: auto; }
        .runs-main section { margin-bottom: 2rem; }
        .runs-main h3 { color: #b8b8d0; font-size: 1rem; }
        .runs-meta { display: flex; flex-wrap: wrap; gap: 1rem; margin: 1rem 0; font-size: 0.85rem; color: #8888a0; }
        .runs-controls button { background: #2a2a3a; color: #e8e8ef; border: none; padding: 0.4rem 0.8rem; border-radius: 6px; margin-right: 0.5rem; cursor: pointer; }
        .runs-tree { display: flex; flex-wrap: wrap; gap: 0.75rem; }
        .runs-tree-node { background: #12121a; border: 1px solid #2a2a3a; padding: 0.75rem 1rem; border-radius: 8px; font-size: 0.85rem; }
        .runs-hyp { background: #12121a; border: 1px solid #2a2a3a; padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem; font-size: 0.9rem; }
        .runs-hyp.rejected { opacity: 0.5; border-color: #4a3030; }
        .runs-badge { font-size: 0.7rem; background: #2a2a4a; color: #9ca8ff; padding: 0.1rem 0.4rem; border-radius: 4px; margin-right: 0.5rem; }
        .runs-failure { background: #1a1010; border: 1px solid #4a3030; padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem; }
        .runs-timeline { list-style: none; padding: 0; }
        .runs-timeline li { padding: 0.5rem 0; border-bottom: 1px solid #1e1e2e; font-size: 0.85rem; }
        .runs-phase { color: #7c8cff; margin-right: 0.5rem; font-weight: 500; }
        .runs-report { background: #12121a; border: 1px solid #2a2a3a; padding: 1rem; border-radius: 8px; white-space: pre-wrap; font-size: 0.85rem; line-height: 1.6; overflow-x: auto; }
        .runs-empty, .runs-muted { color: #666680; }
      `}</style>
    </div>
  );
}
