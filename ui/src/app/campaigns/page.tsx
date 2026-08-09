"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Campaign {
  campaign_id: string;
  name: string;
  objective: string;
  phase?: string;
  status?: string;
}

interface Dashboard {
  phase?: string;
  cycle_number?: number;
  next_compute?: string;
  [key: string]: unknown;
}

export default function CampaignsPage() {
  const [token, setToken] = useState("axiom-dev-token");
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [selected, setSelected] = useState<Campaign | null>(null);
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [name, setName] = useState("");
  const [objective, setObjective] = useState("");
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

  const loadCampaigns = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/frce/campaigns`, { headers: headers() });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setCampaigns(data.campaigns || data || []);
    } catch (e) {
      setStatus(`Failed to load campaigns: ${e}`);
    }
  }, [headers]);

  useEffect(() => {
    loadCampaigns();
  }, [loadCampaigns]);

  async function createCampaign(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setStatus(null);
    try {
      const res = await fetch(`${API_BASE}/frce/campaigns`, {
        method: "POST",
        headers: headers(),
        body: JSON.stringify({
          name,
          objective,
          problem_definition: objective,
        }),
      });
      if (!res.ok) throw new Error(await res.text());
      const campaign = await res.json();
      setSelected(campaign);
      setName("");
      setObjective("");
      await loadCampaigns();
      setStatus(`Created campaign ${campaign.campaign_id}`);
    } catch (err) {
      setStatus(`Create failed: ${err}`);
    } finally {
      setLoading(false);
    }
  }

  async function runStep(step: "scope" | "plan" | "cycle") {
    if (!selected) return;
    setLoading(true);
    setStatus(null);
    try {
      const res = await fetch(
        `${API_BASE}/frce/campaigns/${selected.campaign_id}/${step}`,
        { method: "POST", headers: headers() }
      );
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      if (step === "cycle") {
        setStatus(`Cycle complete: ${JSON.stringify(data).slice(0, 200)}`);
      } else {
        setSelected(data);
        setStatus(`${step} complete`);
      }
      const dash = await fetch(
        `${API_BASE}/frce/campaigns/${selected.campaign_id}/dashboard`,
        { headers: headers() }
      );
      if (dash.ok) setDashboard(await dash.json());
      await loadCampaigns();
    } catch (err) {
      setStatus(`${step} failed: ${err}`);
    } finally {
      setLoading(false);
    }
  }

  async function openCampaign(c: Campaign) {
    setSelected(c);
    setDashboard(null);
    try {
      const res = await fetch(`${API_BASE}/frce/campaigns/${c.campaign_id}/dashboard`, {
        headers: headers(),
      });
      if (res.ok) setDashboard(await res.json());
    } catch {
      /* ignore */
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
          <Link className="nav-cta" href="/campaigns">
            Campaigns
          </Link>
        </nav>
      </header>

      <section className="section" style={{ paddingTop: 40 }}>
        <p className="section-label">Research campaigns</p>
        <h1 className="section-title">Frontier campaigns</h1>
        <p className="section-subtitle">
          Create a campaign, scope it, plan strategies, then run a research cycle against the
          real FRCE API. No simulated UI actions.
        </p>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginTop: 32 }}>
          <form className="auth-form" onSubmit={createCampaign}>
            <h2>Create campaign</h2>
            <label className="auth-field">
              <span>Name</span>
              <input required value={name} onChange={(e) => setName(e.target.value)} />
            </label>
            <label className="auth-field">
              <span>Objective</span>
              <input
                required
                value={objective}
                onChange={(e) => setObjective(e.target.value)}
                placeholder="What should AXIOM investigate?"
              />
            </label>
            <button className="btn btn-primary" type="submit" disabled={loading}>
              {loading ? "Working…" : "Create campaign →"}
            </button>
          </form>

          <div>
            <h2>Your campaigns</h2>
            <ul style={{ listStyle: "none", padding: 0, marginTop: 12 }}>
              {campaigns.map((c) => (
                <li key={c.campaign_id} style={{ marginBottom: 8 }}>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    style={{ width: "100%", textAlign: "left" }}
                    onClick={() => openCampaign(c)}
                  >
                    {c.name}
                    <div style={{ fontSize: 12, opacity: 0.7 }}>{c.campaign_id}</div>
                  </button>
                </li>
              ))}
              {campaigns.length === 0 && <p className="auth-footnote">No campaigns yet.</p>}
            </ul>
          </div>
        </div>

        {selected && (
          <div style={{ marginTop: 40 }}>
            <h2>{selected.name}</h2>
            <p style={{ color: "var(--text-secondary)" }}>{selected.objective}</p>
            <div style={{ display: "flex", gap: 12, marginTop: 16, flexWrap: "wrap" }}>
              <button className="btn btn-secondary" type="button" disabled={loading} onClick={() => runStep("scope")}>
                Scope
              </button>
              <button className="btn btn-secondary" type="button" disabled={loading} onClick={() => runStep("plan")}>
                Plan
              </button>
              <button className="btn btn-primary" type="button" disabled={loading} onClick={() => runStep("cycle")}>
                Run cycle →
              </button>
            </div>
            {dashboard && (
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
                {JSON.stringify(dashboard, null, 2)}
              </pre>
            )}
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
