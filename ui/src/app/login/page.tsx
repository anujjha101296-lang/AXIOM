"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Mode = "login" | "signup";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>("signup");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const path = mode === "signup" ? "/auth/signup" : "/auth/login";
      const body: Record<string, string> = { email, password };
      if (mode === "signup" && displayName.trim()) {
        body.display_name = displayName.trim();
      }
      const resp = await fetch(`${API_BASE}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await resp.json().catch(() => ({}));
      if (!resp.ok) {
        setError(typeof data.detail === "string" ? data.detail : "Authentication failed");
        return;
      }
      if (data.access_token) {
        localStorage.setItem("axiom_access_token", data.access_token);
        if (data.user) {
          localStorage.setItem("axiom_user", JSON.stringify(data.user));
        }
      }
      router.push("/research");
    } catch {
      setError("Could not reach API. Is the server running on localhost:8000?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <a className="skip-link" href="#auth-form">
        Skip to form
      </a>
      <header className="site-header">
        <Link className="wordmark" href="/" aria-label="AXIOM home">
          <span className="wordmark-mark" aria-hidden="true">
            A
          </span>
          <span>AXIOM</span>
        </Link>
        <nav aria-label="Primary navigation">
          <Link href="/">Home</Link>
          <Link href="/campaigns">Campaigns</Link>
          <Link href="/experiments">Experiments</Link>
          <Link className="nav-cta" href="/research">
            Research Workspace
          </Link>
        </nav>
      </header>

      <section className="auth-panel" id="auth-form" aria-labelledby="auth-title">
        <p className="section-label">Account</p>
        <h1 id="auth-title">{mode === "signup" ? "Create your account" : "Sign in"}</h1>
        <p className="auth-lead">
          Sign up to use the research workspace with your own credentials. Local
          development still accepts the static bearer token.
        </p>

        <div className="auth-tabs" role="tablist">
          <button
            type="button"
            role="tab"
            aria-selected={mode === "signup"}
            className={mode === "signup" ? "auth-tab active" : "auth-tab"}
            onClick={() => setMode("signup")}
          >
            Sign up
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={mode === "login"}
            className={mode === "login" ? "auth-tab active" : "auth-tab"}
            onClick={() => setMode("login")}
          >
            Sign in
          </button>
        </div>

        <form className="auth-form" onSubmit={onSubmit}>
          {mode === "signup" && (
            <label className="auth-field">
              <span>Display name</span>
              <input
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                placeholder="Optional"
                autoComplete="name"
              />
            </label>
          )}
          <label className="auth-field">
            <span>Email</span>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@university.edu"
              autoComplete="email"
            />
          </label>
          <label className="auth-field">
            <span>Password</span>
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 8 characters"
              autoComplete={mode === "signup" ? "new-password" : "current-password"}
            />
          </label>
          {error && (
            <p className="auth-error" role="alert">
              {error}
            </p>
          )}
          <button className="btn btn-primary auth-submit" type="submit" disabled={loading}>
            {loading ? "Working…" : mode === "signup" ? "Create account →" : "Sign in →"}
          </button>
        </form>

        <p className="auth-footnote">
          After sign-in you will enter the research workspace. Dev token{" "}
          <code className="inline-code">axiom-dev-token</code> still works for local API
          testing.
        </p>
      </section>
    </main>
  );
}
