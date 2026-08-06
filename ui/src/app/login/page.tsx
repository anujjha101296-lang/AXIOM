"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import React, { useEffect, useState } from "react";
import {
  API_BASE,
  AuthResponse,
  getStoredToken,
  parseApiError,
  storeAuth,
} from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (getStoredToken()) {
      router.replace("/research");
    }
  }, [router]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const endpoint = mode === "login" ? "/auth/login" : "/auth/register";
      const body =
        mode === "login"
          ? { email, password }
          : { email, password, name };

      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        throw new Error(await parseApiError(res));
      }

      const data: AuthResponse = await res.json();
      storeAuth(data.access_token, data.user);
      router.push("/research");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card" role="main">
        <Link href="/" className="auth-back">
          ← AXIOM
        </Link>
        <h1>{mode === "login" ? "Sign in" : "Create account"}</h1>
        <p className="auth-subtitle">
          {mode === "login"
            ? "Access your research projects, papers, and notes."
            : "Register to start organizing your research in AXIOM."}
        </p>

        <form onSubmit={submit} aria-label={mode === "login" ? "Sign in form" : "Registration form"}>
          {mode === "register" && (
            <label className="auth-field">
              <span>Name</span>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                autoComplete="name"
                required
                disabled={loading}
              />
            </label>
          )}
          <label className="auth-field">
            <span>Email</span>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              required
              disabled={loading}
            />
          </label>
          <label className="auth-field">
            <span>Password</span>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete={mode === "login" ? "current-password" : "new-password"}
              minLength={mode === "register" ? 8 : 1}
              required
              disabled={loading}
            />
            {mode === "register" && (
              <small className="auth-hint">At least 8 characters</small>
            )}
          </label>

          {error && (
            <div className="auth-error" role="alert" aria-live="assertive">
              {error}
            </div>
          )}

          <button type="submit" className="auth-submit" disabled={loading} aria-busy={loading}>
            {loading ? "Please wait…" : mode === "login" ? "Sign in" : "Create account"}
          </button>
        </form>

        <p className="auth-switch">
          {mode === "login" ? (
            <>
              New to AXIOM?{" "}
              <button type="button" onClick={() => { setMode("register"); setError(null); }}>
                Create an account
              </button>
            </>
          ) : (
            <>
              Already have an account?{" "}
              <button type="button" onClick={() => { setMode("login"); setError(null); }}>
                Sign in
              </button>
            </>
          )}
        </p>
      </div>

      <style jsx>{`
        .auth-page {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #0a0a0f;
          color: #e8e8ef;
          font-family: Inter, system-ui, sans-serif;
          padding: 2rem;
        }
        .auth-card {
          width: 100%;
          max-width: 400px;
          background: #12121a;
          border: 1px solid #2a2a3a;
          border-radius: 12px;
          padding: 2rem;
        }
        .auth-back {
          color: #7c8cff;
          text-decoration: none;
          font-size: 0.85rem;
        }
        h1 {
          margin: 1rem 0 0.5rem;
          font-size: 1.5rem;
        }
        .auth-subtitle {
          color: #8888a0;
          font-size: 0.9rem;
          margin: 0 0 1.5rem;
        }
        .auth-field {
          display: block;
          margin-bottom: 1rem;
        }
        .auth-field span {
          display: block;
          font-size: 0.8rem;
          color: #8888a0;
          margin-bottom: 0.35rem;
        }
        .auth-field input {
          width: 100%;
          box-sizing: border-box;
          background: #0a0a0f;
          border: 1px solid #2a2a3a;
          color: #e8e8ef;
          padding: 0.6rem 0.75rem;
          border-radius: 6px;
          font-size: 0.95rem;
        }
        .auth-field input:focus {
          outline: 2px solid #4f5dff;
          outline-offset: 1px;
        }
        .auth-hint {
          display: block;
          margin-top: 0.25rem;
          color: #666680;
          font-size: 0.75rem;
        }
        .auth-error {
          background: #2a1515;
          border: 1px solid #5a3030;
          color: #ff9a9a;
          padding: 0.75rem;
          border-radius: 6px;
          font-size: 0.85rem;
          margin-bottom: 1rem;
        }
        .auth-submit {
          width: 100%;
          background: #4f5dff;
          color: white;
          border: none;
          padding: 0.75rem;
          border-radius: 6px;
          font-size: 0.95rem;
          cursor: pointer;
          font-weight: 500;
        }
        .auth-submit:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
        .auth-switch {
          margin-top: 1.5rem;
          text-align: center;
          font-size: 0.85rem;
          color: #8888a0;
        }
        .auth-switch button {
          background: none;
          border: none;
          color: #7c8cff;
          cursor: pointer;
          text-decoration: underline;
          font-size: inherit;
        }
      `}</style>
    </div>
  );
}
