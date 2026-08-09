"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Investigation {
  discovery_id: string;
  research_question: string;
  status: string;
  novelty?: { status?: string; search_notes?: string };
  hypotheses?: Array<{ statement: string; rejected?: boolean }>;
  report?: Record<string, unknown>;
}

export default function DiscoveryPage() {
  const [token, setToken] = useState("axiom-dev-token");
  const [question, setQuestion] = useState(
    "Does addition identity n+0=n hold for small integers?"
  );
  const [seed, setSeed] = useState(
    "It is well known that for integers n, n+0=n. Open question: edge notation variants."
  );
  const [items, setItems] = useState<Investigation[]>([]);
  const [selected, setSelected] = useState<Investigation | null>(null);
  const [cycleResult, setCycleResult] = useState<Record<string, unknown> | null>(null);
  const [bench, setBench] = useState<Record<string, unknown> | null>(null);
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

  const load = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/discovery/investigations`, { headers: headers() });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setItems(data.investigations || []);
    } catch (e) {
      setStatus(`Load failed: ${e}`);
    }
  }, [headers]);

  useEffect(() => {
    load();
  }, [load]);

  async function createInvestigation(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setStatus(null);
    try {
      const res = await fetch(`${API_BASE}/discovery/investigations`, {
        method: "POST",
        headers: headers(),
        body: JSON.stringify({
          research_question: question,
          seed_text: seed,
          knowledge_context: seed,
        }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setSelected(data);
      setStatus(`Created ${data.discovery_id} (${data.status})`);
      await load();
    } catch (err) {
      setStatus(`Create failed: ${err}`);
    } finally {
      setLoading(false);
    }
  }

  async function runCycle() {
    if (!selected) return;
    setLoading(true);
    setStatus(null);
    try {
      const res = await fetch(
        `${API_BASE}/discovery/investigations/${selected.discovery_id}/cycle`,
        { method: "POST", headers: headers() }
      );
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setCycleResult(data);
      const refreshed = await fetch(
        `${API_BASE}/discovery/investigations/${selected.discovery_id}`,
        { headers: headers() }
      );
      if (refreshed.ok) setSelected(await refreshed.json());
      setStatus(`Cycle complete — status=${data.status}`);
      await load();
    } catch (err) {
      setStatus(`Cycle failed: ${err}`);
    } finally {
      setLoading(false);
    }
  }

  async function runBenchmarks() {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/discovery/benchmarks/run`, {
        method: "POST",
        headers: headers(),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setBench(data);
      setStatus(
        `Benchmarks: ${data.passed}/${data.total} passed; FDR=${data.false_discovery_rate}`
      );
    } catch (err) {
      setStatus(`Benchmarks failed: ${err}`);
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
          <Link href="/sources">Sources</Link>
          <Link className="nav-cta" href="/discovery">
            Discovery
          </Link>
        </nav>
      </header>

      <section className="section" style={{ paddingTop: 40 }}>
        <p className="section-label">Scientific Discovery Engine</p>
        <h1 className="section-title">Investigate — do not invent</h1>
        <p className="section-subtitle">
          Gap → opportunity → competing hypotheses → predictions → experiment → counterexample →
          skeptical attack. Computational evidence is not proof. Missing papers are not novelty.
        </p>

        <form className="auth-form" onSubmit={createInvestigation} style={{ maxWidth: 720, marginTop: 32 }}>
          <label className="auth-field">
            <span>Research question</span>
            <input required value={question} onChange={(e) => setQuestion(e.target.value)} />
          </label>
          <label className="auth-field">
            <span>Seed knowledge (optional)</span>
            <textarea rows={4} value={seed} onChange={(e) => setSeed(e.target.value)} />
          </label>
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? "Working…" : "Create investigation →"}
          </button>
        </form>

        <div style={{ display: "flex", gap: 12, marginTop: 20, flexWrap: "wrap" }}>
          <button className="btn btn-secondary" type="button" disabled={loading || !selected} onClick={runCycle}>
            Run discovery cycle
          </button>
          <button className="btn btn-secondary" type="button" disabled={loading} onClick={runBenchmarks}>
            Run deterministic benchmarks
          </button>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginTop: 32 }}>
          <div>
            <h2>Investigations</h2>
            <ul style={{ listStyle: "none", padding: 0, marginTop: 12 }}>
              {items.map((d) => (
                <li key={d.discovery_id} style={{ marginBottom: 8 }}>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    style={{ width: "100%", textAlign: "left" }}
                    onClick={() => {
                      setSelected(d);
                      setCycleResult(null);
                    }}
                  >
                    {d.research_question.slice(0, 80)}
                    <div style={{ fontSize: 12, opacity: 0.7 }}>
                      {d.status} · {d.discovery_id}
                    </div>
                  </button>
                </li>
              ))}
              {items.length === 0 && <p className="auth-footnote">No investigations yet.</p>}
            </ul>
          </div>

          <div>
            {selected && (
              <>
                <h2>{selected.status}</h2>
                <p style={{ color: "var(--text-secondary)" }}>{selected.research_question}</p>
                <p className="auth-footnote">
                  Novelty: {selected.novelty?.status || "n/a"}
                </p>
                <ul style={{ marginTop: 12, paddingLeft: 18, fontSize: 13 }}>
                  {(selected.hypotheses || [])
                    .filter((h) => !h.rejected)
                    .slice(0, 4)
                    .map((h) => (
                      <li key={h.statement}>{h.statement}</li>
                    ))}
                </ul>
              </>
            )}
          </div>
        </div>

        {cycleResult && (
          <pre
            style={{
              marginTop: 24,
              padding: 16,
              background: "var(--bg-card)",
              border: "1px solid var(--border)",
              borderRadius: 12,
              overflow: "auto",
              fontSize: 12,
            }}
          >
            {JSON.stringify(cycleResult, null, 2)}
          </pre>
        )}

        {bench && (
          <pre
            style={{
              marginTop: 24,
              padding: 16,
              background: "var(--bg-card)",
              border: "1px solid var(--border)",
              borderRadius: 12,
              overflow: "auto",
              fontSize: 12,
            }}
          >
            {JSON.stringify(bench, null, 2)}
          </pre>
        )}

        {status && (
          <p className="auth-footnote" role="status" style={{ marginTop: 24 }}>
            {status}
          </p>
        )}

        <label className="auth-field" style={{ marginTop: 32, maxWidth: 480 }}>
          <span>API token</span>
          <input value={token} onChange={(e) => setToken(e.target.value)} />
        </label>
      </section>
    </main>
  );
}
