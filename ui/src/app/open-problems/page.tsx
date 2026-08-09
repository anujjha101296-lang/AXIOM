"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function OpenProblemsPage() {
  const [token, setToken] = useState("axiom-dev-token");
  const [title, setTitle] = useState("Known-false odd primes claim");
  const [statement, setStatement] = useState(
    "Is it true that all odd numbers greater than 1 are prime (known false)?"
  );
  const [known, setKnown] = useState(
    "Claim already disproven / known false. Composite 9 is a counterexample."
  );
  const [items, setItems] = useState<Array<Record<string, unknown>>>([]);
  const [selected, setSelected] = useState<Record<string, unknown> | null>(null);
  const [cycle, setCycle] = useState<Record<string, unknown> | null>(null);
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
    const res = await fetch(`${API_BASE}/open-problems`, { headers: headers() });
    if (res.ok) {
      const data = await res.json();
      setItems(data.problems || []);
    }
  }, [headers]);

  useEffect(() => {
    load();
  }, [load]);

  async function onCreate(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setStatus(null);
    try {
      const res = await fetch(`${API_BASE}/open-problems`, {
        method: "POST",
        headers: headers(),
        body: JSON.stringify({
          title,
          informal_statement: statement,
          known_info: known,
          stage_level: 1,
          domain: "mathematics",
          research_objective: "Counterexample-first investigation of known-outcome claim",
        }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setSelected(data);
      setStatus(`Created ${data.problem_id}`);
      await load();
    } catch (err) {
      setStatus(`Create failed: ${err}`);
    } finally {
      setLoading(false);
    }
  }

  async function runCycle() {
    if (!selected?.problem_id) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/open-problems/${selected.problem_id}/cycle`, {
        method: "POST",
        headers: headers(),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setCycle(data);
      const refreshed = await fetch(`${API_BASE}/open-problems/${selected.problem_id}`, {
        headers: headers(),
      });
      if (refreshed.ok) setSelected(await refreshed.json());
      setStatus(`Cycle status: ${data.research_status}`);
    } catch (err) {
      setStatus(`Cycle failed: ${err}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ maxWidth: 960, margin: "0 auto", padding: "2rem 1.25rem", fontFamily: "Georgia, serif" }}>
      <header style={{ display: "flex", justifyContent: "space-between", gap: "1rem", flexWrap: "wrap" }}>
        <div>
          <p style={{ margin: 0, letterSpacing: "0.08em", fontSize: "0.75rem" }}>AXIOM · OPEN PROBLEM LAB</p>
          <h1 style={{ margin: "0.35rem 0" }}>Open Problem Research Lab</h1>
          <p style={{ margin: 0, maxWidth: 40rem }}>
            Persistent investigation machinery. Not a Millennium claim. Counterexample-first for
            conjectures.
          </p>
        </div>
        <nav style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
          <Link href="/discovery">Discovery</Link>
          <Link href="/campaigns">Campaigns</Link>
          <Link href="/arena">Arena</Link>
          <Link href="/">Home</Link>
        </nav>
      </header>

      <form onSubmit={onCreate} style={{ marginTop: "2rem", display: "grid", gap: "0.75rem" }}>
        <label>
          Title
          <input value={title} onChange={(e) => setTitle(e.target.value)} style={{ width: "100%" }} />
        </label>
        <label>
          Statement
          <textarea
            value={statement}
            onChange={(e) => setStatement(e.target.value)}
            rows={3}
            style={{ width: "100%" }}
          />
        </label>
        <label>
          Known information
          <textarea value={known} onChange={(e) => setKnown(e.target.value)} rows={2} style={{ width: "100%" }} />
        </label>
        <button disabled={loading} type="submit">
          Create Level-1 problem
        </button>
      </form>

      {status && <p style={{ marginTop: "1rem" }}>{status}</p>}

      <section style={{ marginTop: "1.5rem" }}>
        <h2>Problems</h2>
        <ul>
          {items.map((p) => (
            <li key={String(p.problem_id)}>
              <button type="button" onClick={() => setSelected(p)}>
                {String(p.title)} · {String(p.research_status)}
              </button>
            </li>
          ))}
        </ul>
      </section>

      {selected && (
        <section style={{ marginTop: "1.5rem" }}>
          <h2>Selected</h2>
          <p>
            {String(selected.problem_id)} · status {String(selected.research_status)} · stage{" "}
            {String(selected.stage_level)}
          </p>
          <p>Campaigns: {JSON.stringify(selected.campaign_ids)}</p>
          <p>Discoveries: {JSON.stringify(selected.discovery_ids)}</p>
          <button disabled={loading} type="button" onClick={runCycle}>
            Run investigation cycle
          </button>
          {cycle && (
            <pre style={{ whiteSpace: "pre-wrap", marginTop: "1rem", fontSize: "0.85rem" }}>
              {JSON.stringify(cycle, null, 2)}
            </pre>
          )}
        </section>
      )}
    </main>
  );
}
