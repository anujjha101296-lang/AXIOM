"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ArenaPage() {
  const [token, setToken] = useState("axiom-dev-token");
  const [catalog, setCatalog] = useState<{ count?: number; dataset_version?: string } | null>(
    null
  );
  const [runs, setRuns] = useState<Array<Record<string, unknown>>>([]);
  const [latest, setLatest] = useState<Record<string, unknown> | null>(null);
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

  const refresh = useCallback(async () => {
    try {
      const [c, r, ready] = await Promise.all([
        fetch(`${API_BASE}/arena/catalog`, { headers: headers() }),
        fetch(`${API_BASE}/arena/runs`, { headers: headers() }),
        fetch(`${API_BASE}/arena/readiness`, { headers: headers() }),
      ]);
      if (c.ok) setCatalog(await c.json());
      if (r.ok) {
        const data = await r.json();
        setRuns(data.runs || []);
      }
      if (ready.ok) setLatest(await ready.json());
    } catch (e) {
      setStatus(`Load failed: ${e}`);
    }
  }, [headers]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function runSuite(isBaseline: boolean) {
    setLoading(true);
    setStatus(null);
    try {
      const res = await fetch(`${API_BASE}/arena/run`, {
        method: "POST",
        headers: headers(),
        body: JSON.stringify({
          is_baseline: isBaseline,
          notes: isBaseline ? "Recorded baseline" : "Arena run",
        }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setLatest({
        run_id: data.run?.run_id,
        git_commit: data.run?.git_commit,
        readiness: data.run?.readiness,
        dimension_scores: data.run?.dimension_scores,
        weaknesses: data.run?.weaknesses,
        summary: data.run?.summary,
        comparison: data.comparison,
      });
      setStatus(
        `Run ${data.run?.run_id}: passed ${data.run?.summary?.passed}/${data.run?.summary?.total}`
      );
      await refresh();
    } catch (e) {
      setStatus(`Run failed: ${e}`);
    } finally {
      setLoading(false);
    }
  }

  const dims = (latest?.dimension_scores || {}) as Record<string, number>;
  const readiness = (latest?.readiness || {}) as Record<string, unknown>;
  const weaknesses = (latest?.weaknesses || []) as Array<Record<string, unknown>>;

  return (
    <main style={{ maxWidth: 960, margin: "0 auto", padding: "2rem 1.25rem", fontFamily: "Georgia, serif" }}>
      <header style={{ display: "flex", justifyContent: "space-between", gap: "1rem", flexWrap: "wrap" }}>
        <div>
          <p style={{ margin: 0, letterSpacing: "0.08em", fontSize: "0.75rem" }}>AXIOM · ARENA</p>
          <h1 style={{ margin: "0.35rem 0" }}>Research Benchmark Arena</h1>
          <p style={{ margin: 0, maxWidth: 42rem }}>
            Measured scientific capability scores. Ground-truth answers are not shown. Higher tiers
            require gate evidence.
          </p>
        </div>
        <nav style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
          <Link href="/discovery">Discovery</Link>
          <Link href="/research">Research</Link>
          <Link href="/">Home</Link>
        </nav>
      </header>

      <section style={{ marginTop: "2rem" }}>
        <p>
          Dataset: <strong>{catalog?.dataset_version || "…"}</strong> · Cases:{" "}
          <strong>{catalog?.count ?? "…"}</strong>
        </p>
        <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
          <button disabled={loading} onClick={() => runSuite(true)}>
            Record baseline
          </button>
          <button disabled={loading} onClick={() => runSuite(false)}>
            Run suite
          </button>
        </div>
        {status && <p style={{ marginTop: "0.75rem" }}>{status}</p>}
      </section>

      <section style={{ marginTop: "2rem" }}>
        <h2>Latest readiness</h2>
        <p>
          Unlocked tier:{" "}
          <strong>{String((readiness as { highest_unlocked_tier?: number }).highest_unlocked_tier ?? "—")}</strong>
          {" · "}
          Millennium auto-claim: <strong>false</strong>
        </p>
        {latest?.summary && (
          <p>
            Mean score: {String((latest.summary as { mean_score?: number }).mean_score)} · Passed:{" "}
            {String((latest.summary as { passed?: number }).passed)}/
            {String((latest.summary as { total?: number }).total)}
          </p>
        )}
      </section>

      <section style={{ marginTop: "1.5rem" }}>
        <h2>Dimension scores</h2>
        <ul>
          {Object.entries(dims)
            .slice(0, 16)
            .map(([k, v]) => (
              <li key={k}>
                {k}: {typeof v === "number" ? v.toFixed(3) : String(v)}
              </li>
            ))}
        </ul>
      </section>

      <section style={{ marginTop: "1.5rem" }}>
        <h2>Top weaknesses</h2>
        <ul>
          {weaknesses.length === 0 && <li>No run yet.</li>}
          {weaknesses.map((w, i) => (
            <li key={i}>
              {String(w.kind)} / {String(w.name)} — severity {String(w.severity)} (value{" "}
              {String(w.value)})
            </li>
          ))}
        </ul>
      </section>

      <section style={{ marginTop: "1.5rem" }}>
        <h2>Recent runs</h2>
        <ul>
          {runs.map((r) => (
            <li key={String(r.run_id)}>
              {String(r.run_id)} · mean {String(r.mean_score)} · commit{" "}
              {String(r.git_commit || "").slice(0, 8)}
              {r.is_baseline ? " · BASELINE" : ""}
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
