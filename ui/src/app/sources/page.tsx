"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface AcquireResult {
  acquisition_id: string;
  status: string;
  duplicate?: boolean;
  untrusted?: boolean;
  retrieved_at?: string | null;
  source_url?: string | null;
  sources?: string[];
  entities?: string[];
  instruction_pattern_hits?: string[];
}

interface SourceRow {
  source_id: string;
  title: string;
  source_type: string;
  quality_tier?: string;
  location?: string | null;
  content_hash?: string | null;
  metadata?: Record<string, unknown>;
  created_at?: string;
}

export default function SourcesPage() {
  const [token, setToken] = useState("axiom-dev-token");
  const [url, setUrl] = useState("https://arxiv.org/abs/1901.00001");
  const [question, setQuestion] = useState("");
  const [hosts, setHosts] = useState<string[]>([]);
  const [sources, setSources] = useState<SourceRow[]>([]);
  const [last, setLast] = useState<AcquireResult | null>(null);
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
      const [h, s] = await Promise.all([
        fetch(`${API_BASE}/skai/allowed-hosts`, { headers: headers() }),
        fetch(`${API_BASE}/skai/sources?limit=50`, { headers: headers() }),
      ]);
      if (h.ok) {
        const data = await h.json();
        setHosts(data.allowed_hosts || []);
      }
      if (s.ok) {
        const data = await s.json();
        setSources(data.sources || []);
      }
    } catch (e) {
      setStatus(`Failed to load sources: ${e}`);
    }
  }, [headers]);

  useEffect(() => {
    load();
  }, [load]);

  async function onAcquire(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setStatus(null);
    setLast(null);
    try {
      const res = await fetch(`${API_BASE}/skai/acquire-url`, {
        method: "POST",
        headers: headers(),
        body: JSON.stringify({
          url,
          research_question: question || undefined,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(typeof data.detail === "string" ? data.detail : JSON.stringify(data));
      }
      setLast(data);
      setStatus(
        data.duplicate
          ? `Duplicate source reused (${data.sources?.[0]})`
          : `Acquired untrusted source (${data.sources?.[0]})`
      );
      await load();
    } catch (err) {
      setStatus(`Acquire failed: ${err}`);
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
          <Link className="nav-cta" href="/sources">
            Sources
          </Link>
        </nav>
      </header>

      <section className="section" style={{ paddingTop: 40 }}>
        <p className="section-label">Controlled internet research</p>
        <h1 className="section-title">Acquire web sources</h1>
        <p className="section-subtitle">
          Fetch allowlisted HTTPS pages, extract text, store provenance with retrieval time, and
          mark content as UNTRUSTED. Webpage text never becomes system instructions.
        </p>

        <form className="auth-form" onSubmit={onAcquire} style={{ maxWidth: 720, marginTop: 32 }}>
          <label className="auth-field">
            <span>URL (HTTPS, allowlisted host)</span>
            <input required value={url} onChange={(e) => setUrl(e.target.value)} />
          </label>
          <label className="auth-field">
            <span>Research question (optional)</span>
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="What should AXIOM look for in this source?"
            />
          </label>
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? "Fetching…" : "Acquire URL →"}
          </button>
        </form>

        {hosts.length > 0 && (
          <p className="auth-footnote" style={{ marginTop: 16 }}>
            Allowed hosts: {hosts.join(", ")}
          </p>
        )}

        {last && (
          <pre
            style={{
              marginTop: 24,
              padding: 16,
              background: "var(--bg-card)",
              border: "1px solid var(--border)",
              borderRadius: 12,
              overflow: "auto",
              fontSize: 12,
              maxWidth: 900,
            }}
          >
            {JSON.stringify(last, null, 2)}
          </pre>
        )}

        <h2 style={{ marginTop: 40 }}>Stored sources</h2>
        <ul style={{ listStyle: "none", padding: 0, marginTop: 12, maxWidth: 900 }}>
          {sources.map((s) => (
            <li
              key={s.source_id}
              style={{
                marginBottom: 12,
                padding: 16,
                border: "1px solid var(--border)",
                borderRadius: 12,
                background: "var(--bg-card)",
              }}
            >
              <strong>{s.title}</strong>
              <div style={{ fontSize: 12, opacity: 0.75, marginTop: 4 }}>
                {s.source_type} · {s.quality_tier || "unverified"} · {s.source_id}
                {Boolean(s.metadata?.untrusted) ? " · UNTRUSTED" : ""}
              </div>
              {(s.location || (s.metadata?.final_url as string | undefined)) && (
                <div style={{ fontSize: 12, marginTop: 4 }}>
                  {String(s.location || s.metadata?.final_url)}
                </div>
              )}
              {s.metadata?.retrieved_at ? (
                <div style={{ fontSize: 12, opacity: 0.7 }}>
                  retrieved {String(s.metadata.retrieved_at)}
                </div>
              ) : null}
            </li>
          ))}
          {sources.length === 0 && <p className="auth-footnote">No sources yet.</p>}
        </ul>

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
