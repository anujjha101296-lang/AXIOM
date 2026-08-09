"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const SAFE_DEFAULT_CODE = `print("AXIOM SEC experiment")
for n in range(5):
    assert n + 0 == n
print("OK")
`;

interface Experiment {
  experiment_id: string;
  status: string;
  created_at?: string;
  updated_at?: string;
  spec?: {
    research_question?: string;
    hypothesis?: string;
    objective?: string;
    code?: string | null;
  };
  results?: Record<string, unknown>;
  verification_status?: string;
  evidence_class?: string;
}

export default function ExperimentsPage() {
  const [token, setToken] = useState("axiom-dev-token");
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [selected, setSelected] = useState<Experiment | null>(null);
  const [runResult, setRunResult] = useState<Record<string, unknown> | null>(null);
  const [question, setQuestion] = useState("");
  const [hypothesis, setHypothesis] = useState("");
  const [objective, setObjective] = useState("");
  const [code, setCode] = useState(SAFE_DEFAULT_CODE);
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    try {
      const saved = localStorage.getItem("axiom_access_token");
      if (saved) setToken(saved);
    } catch {
      /* ignore */
    }
  }, []);

  const headers = useCallback(
    () => ({
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    }),
    [token]
  );

  const loadExperiments = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/experiments/`, { headers: headers() });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setExperiments(data.experiments || []);
    } catch (e) {
      setStatus(`Failed to load experiments: ${e}`);
    }
  }, [headers]);

  useEffect(() => {
    loadExperiments();
  }, [loadExperiments]);

  function logout() {
    try {
      localStorage.removeItem("axiom_access_token");
      localStorage.removeItem("axiom_user");
    } catch {
      /* ignore */
    }
    setToken("axiom-dev-token");
    window.location.href = "/login";
  }

  async function createExperiment(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setStatus(null);
    setRunResult(null);
    try {
      const res = await fetch(`${API_BASE}/experiments/`, {
        method: "POST",
        headers: headers(),
        body: JSON.stringify({
          research_question: question,
          hypothesis,
          objective,
          code,
          timeout_seconds: 10,
          random_seed: 42,
        }),
      });
      if (!res.ok) throw new Error(await res.text());
      const experiment = await res.json();
      setSelected(experiment);
      setQuestion("");
      setHypothesis("");
      setObjective("");
      await loadExperiments();
      setStatus(`Created ${experiment.experiment_id} (${experiment.status})`);
    } catch (err) {
      setStatus(`Create failed: ${err}`);
    } finally {
      setLoading(false);
    }
  }

  async function openExperiment(exp: Experiment) {
    setRunResult(null);
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/experiments/${exp.experiment_id}`, {
        headers: headers(),
      });
      if (!res.ok) throw new Error(await res.text());
      setSelected(await res.json());
    } catch (err) {
      setStatus(`Load failed: ${err}`);
    } finally {
      setLoading(false);
    }
  }

  async function runSelected() {
    if (!selected) return;
    setLoading(true);
    setStatus(null);
    try {
      const res = await fetch(`${API_BASE}/experiments/${selected.experiment_id}/run`, {
        method: "POST",
        headers: headers(),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setRunResult(data);
      setStatus(`Run finished: ${data.status}`);
      const refreshed = await fetch(`${API_BASE}/experiments/${selected.experiment_id}`, {
        headers: headers(),
      });
      if (refreshed.ok) setSelected(await refreshed.json());
      await loadExperiments();
    } catch (err) {
      setStatus(`Run failed: ${err}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <header className="site-header">
        <Link className="wordmark" href="/" aria-label="AXIOM home">
          <span className="wordmark-mark" aria-hidden="true">
            A
          </span>
          <span>AXIOM</span>
        </Link>
        <nav aria-label="Primary navigation">
          <Link href="/research">Research</Link>
          <Link href="/campaigns">Campaigns</Link>
          <Link className="nav-cta" href="/experiments">
            Experiments
          </Link>
          <button type="button" className="btn btn-secondary" onClick={logout}>
            Log out
          </button>
        </nav>
      </header>

      <section className="section" style={{ paddingTop: 40 }}>
        <p className="section-label">Scientific Experimentation (SEC)</p>
        <h1 className="section-title">Experiments</h1>
        <p className="section-subtitle">
          Create a sandboxed computational experiment, run it outside the main process, and
          inspect results. Outcomes are computational evidence — not mathematical proof.
        </p>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginTop: 32 }}>
          <form className="auth-form" onSubmit={createExperiment}>
            <h2>Create experiment</h2>
            <label className="auth-field">
              <span>Research question</span>
              <input
                required
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Does n+0 = n for small n?"
              />
            </label>
            <label className="auth-field">
              <span>Hypothesis</span>
              <input
                required
                value={hypothesis}
                onChange={(e) => setHypothesis(e.target.value)}
                placeholder="Addition identity holds"
              />
            </label>
            <label className="auth-field">
              <span>Objective</span>
              <input
                required
                value={objective}
                onChange={(e) => setObjective(e.target.value)}
                placeholder="Verify for n in 0..4"
              />
            </label>
            <label className="auth-field">
              <span>Sandboxed Python code</span>
              <textarea
                required
                rows={8}
                value={code}
                onChange={(e) => setCode(e.target.value)}
                style={{ fontFamily: "ui-monospace, monospace", fontSize: 12 }}
              />
            </label>
            <button className="btn btn-primary" type="submit" disabled={loading}>
              {loading ? "Working…" : "Create experiment →"}
            </button>
          </form>

          <div>
            <h2>Your experiments</h2>
            <ul style={{ listStyle: "none", padding: 0, marginTop: 12 }}>
              {experiments.map((exp) => (
                <li key={exp.experiment_id} style={{ marginBottom: 8 }}>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    style={{ width: "100%", textAlign: "left" }}
                    onClick={() => openExperiment(exp)}
                  >
                    {exp.spec?.research_question || exp.experiment_id}
                    <div style={{ fontSize: 12, opacity: 0.7 }}>
                      {exp.status} · {exp.experiment_id}
                    </div>
                  </button>
                </li>
              ))}
              {experiments.length === 0 && (
                <p className="auth-footnote">No experiments yet.</p>
              )}
            </ul>
          </div>
        </div>

        {selected && (
          <div style={{ marginTop: 40 }}>
            <h2>{selected.spec?.research_question || selected.experiment_id}</h2>
            <p style={{ color: "var(--text-secondary)" }}>
              Status: <strong>{selected.status}</strong>
              {selected.evidence_class ? ` · ${selected.evidence_class}` : ""}
              {selected.verification_status
                ? ` · verification=${selected.verification_status}`
                : ""}
            </p>
            <p style={{ marginTop: 8 }}>{selected.spec?.hypothesis}</p>
            <div style={{ display: "flex", gap: 12, marginTop: 16, flexWrap: "wrap" }}>
              <button
                className="btn btn-primary"
                type="button"
                disabled={loading}
                onClick={runSelected}
              >
                Run in sandbox →
              </button>
            </div>
            {(runResult || selected.results) && (
              <pre
                style={{
                  marginTop: 20,
                  padding: 16,
                  background: "var(--bg-card)",
                  border: "1px solid var(--border)",
                  borderRadius: 12,
                  overflow: "auto",
                  fontSize: 12,
                }}
              >
                {JSON.stringify(runResult || selected.results, null, 2)}
              </pre>
            )}
            <p className="auth-footnote" style={{ marginTop: 12 }}>
              Sandbox evidence is never auto-promoted to VERIFIED or formally verified.
            </p>
          </div>
        )}

        {status && (
          <p className="auth-footnote" role="status" style={{ marginTop: 24 }}>
            {status}
          </p>
        )}

        <label className="auth-field" style={{ marginTop: 32, maxWidth: 480 }}>
          <span>API token (JWT from /login or axiom-dev-token)</span>
          <input value={token} onChange={(e) => setToken(e.target.value)} />
        </label>
      </section>
    </main>
  );
}
