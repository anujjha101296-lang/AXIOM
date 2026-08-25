"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { axiomApi } from "../../../lib/api";

export default function AlphaAdminDashboard() {
  const [stats, setStats] = useState<any>(null);
  const [users, setUsers] = useState<any[]>([]);
  const [inviteEmail, setInviteEmail] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);
  const [msg, setMsg] = useState<string>("");

  useEffect(() => {
    loadAlphaData();
  }, []);

  const loadAlphaData = async () => {
    setLoading(true);
    try {
      const summary = await axiomApi.getAlphaSummary().catch(() => null);
      setStats(summary);

      const userList = await axiomApi.getAlphaUsers().catch(() => []);
      setUsers(userList || []);
    } catch (err) {
      console.error("Error loading alpha data:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inviteEmail) return;
    try {
      await axiomApi.inviteAlphaUser(inviteEmail);
      setMsg(`Successfully invited ${inviteEmail}`);
      setInviteEmail("");
      loadAlphaData();
    } catch (err: any) {
      setMsg(`Invite failed: ${err.message}`);
    }
  };

  const handleStatusChange = async (userId: string, newStatus: string) => {
    try {
      await axiomApi.updateAlphaUserStatus(userId, newStatus);
      loadAlphaData();
    } catch (err: any) {
      alert(`Status update failed: ${err.message}`);
    }
  };

  return (
    <div style={{ fontFamily: "sans-serif", backgroundColor: "#090d16", color: "#f8fafc", minHeight: "100vh", padding: "2rem" }}>
      {/* Navigation Header */}
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem", borderBottom: "1px solid #1e293b", paddingBottom: "1rem" }}>
        <div>
          <h1 style={{ fontSize: "1.75rem", fontWeight: "bold", color: "#f8fafc" }}>AXIOM Private Alpha Administration</h1>
          <p style={{ color: "#94a3b8", fontSize: "0.9rem" }}>Telemetry, Access Control, and Design Partner Feedback Management</p>
        </div>
        <div style={{ display: "flex", gap: "1rem" }}>
          <Link href="/dashboard" style={{ padding: "0.5rem 1rem", backgroundColor: "#1e293b", color: "#e2e8f0", borderRadius: "0.375rem", textDecoration: "none", fontSize: "0.85rem", border: "1px solid #334155" }}>
            ← Research Dashboard
          </Link>
        </div>
      </header>

      {/* Summary Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1.25rem", marginBottom: "2.5rem" }}>
        <div style={{ padding: "1.25rem", backgroundColor: "#0f172a", borderRadius: "0.5rem", border: "1px solid #1e293b" }}>
          <div style={{ color: "#94a3b8", fontSize: "0.8rem", textTransform: "uppercase", fontWeight: "bold" }}>Active Users</div>
          <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#4ade80", marginTop: "0.5rem" }}>{stats?.active_users ?? 0}</div>
        </div>

        <div style={{ padding: "1.25rem", backgroundColor: "#0f172a", borderRadius: "0.5rem", border: "1px solid #1e293b" }}>
          <div style={{ color: "#94a3b8", fontSize: "0.8rem", textTransform: "uppercase", fontWeight: "bold" }}>Total Sessions</div>
          <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#38bdf8", marginTop: "0.5rem" }}>{stats?.total_research_sessions ?? 0}</div>
        </div>

        <div style={{ padding: "1.25rem", backgroundColor: "#0f172a", borderRadius: "0.5rem", border: "1px solid #1e293b" }}>
          <div style={{ color: "#94a3b8", fontSize: "0.8rem", textTransform: "uppercase", fontWeight: "bold" }}>Usefulness Rate</div>
          <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#a855f7", marginTop: "0.5rem" }}>
            {stats?.usefulness_rate_percent != null ? `${stats.usefulness_rate_percent.toFixed(0)}%` : "100%"}
          </div>
        </div>

        <div style={{ padding: "1.25rem", backgroundColor: "#0f172a", borderRadius: "0.5rem", border: "1px solid #1e293b" }}>
          <div style={{ color: "#94a3b8", fontSize: "0.8rem", textTransform: "uppercase", fontWeight: "bold" }}>System Health</div>
          <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#6366f1", marginTop: "0.5rem" }}>OPTIMAL</div>
        </div>
      </div>

      {/* Main Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "2rem" }}>
        {/* Left: User Roster & Invites */}
        <div style={{ padding: "1.5rem", backgroundColor: "#0f172a", borderRadius: "0.5rem", border: "1px solid #1e293b" }}>
          <h2 style={{ fontSize: "1.1rem", fontWeight: "bold", color: "#e2e8f0", marginBottom: "1rem" }}>
            Alpha Access Roster
          </h2>

          {/* Invite Form */}
          <form onSubmit={handleInvite} style={{ display: "flex", gap: "0.5rem", marginBottom: "1.5rem" }}>
            <input
              type="email"
              placeholder="researcher@university.edu"
              value={inviteEmail}
              onChange={(e) => setInviteEmail(e.target.value)}
              style={{ flex: 1, padding: "0.5rem", backgroundColor: "#1e293b", border: "1px solid #334155", color: "#fff", borderRadius: "0.25rem" }}
            />
            <button type="submit" style={{ padding: "0.5rem 1rem", backgroundColor: "#6366f1", color: "#fff", border: "none", borderRadius: "0.25rem", fontWeight: "bold", cursor: "pointer" }}>
              Invite Participant
            </button>
          </form>

          {msg && <div style={{ color: "#818cf8", fontSize: "0.85rem", marginBottom: "1rem" }}>{msg}</div>}

          {/* User Table */}
          <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
            {users.map((u) => (
              <div key={u.user_id} style={{ padding: "0.75rem", backgroundColor: "#1e293b", borderRadius: "0.375rem", border: "1px solid #334155", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <div style={{ fontWeight: "bold", color: "#f8fafc" }}>{u.email}</div>
                  <div style={{ color: "#94a3b8", fontSize: "0.75rem", fontFamily: "monospace" }}>ID: {u.user_id}</div>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                  <span style={{ fontSize: "0.75rem", padding: "0.2rem 0.5rem", borderRadius: "0.25rem", backgroundColor: u.status === "ACTIVE" ? "#065f46" : "#374151", color: u.status === "ACTIVE" ? "#34d399" : "#9ca3af" }}>
                    {u.status}
                  </span>
                  <select
                    value={u.status}
                    onChange={(e) => handleStatusChange(u.user_id, e.target.value)}
                    style={{ padding: "0.3rem", backgroundColor: "#090d16", color: "#fff", border: "1px solid #4b5563", borderRadius: "0.25rem", fontSize: "0.8rem" }}
                  >
                    <option value="INVITED">INVITED</option>
                    <option value="ACTIVE">ACTIVE</option>
                    <option value="SUSPENDED">SUSPENDED</option>
                    <option value="REVOKED">REVOKED</option>
                  </select>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Alpha Configuration & Limits */}
        <div style={{ padding: "1.5rem", backgroundColor: "#0f172a", borderRadius: "0.5rem", border: "1px solid #1e293b" }}>
          <h2 style={{ fontSize: "1.1rem", fontWeight: "bold", color: "#e2e8f0", marginBottom: "1rem" }}>
            Conservative Alpha Limits
          </h2>
          <div style={{ fontSize: "0.85rem", color: "#cbd5e1", display: "flex", flexDirection: "column", gap: "0.75rem" }}>
            <div style={{ padding: "0.5rem", backgroundColor: "#1e293b", borderRadius: "0.25rem", display: "flex", justifyContent: "space-between" }}>
              <span>Missions / Day / User</span>
              <span style={{ fontWeight: "bold", color: "#38bdf8" }}>10</span>
            </div>
            <div style={{ padding: "0.5rem", backgroundColor: "#1e293b", borderRadius: "0.25rem", display: "flex", justifyContent: "space-between" }}>
              <span>LLM Calls / Day / User</span>
              <span style={{ fontWeight: "bold", color: "#38bdf8" }}>100</span>
            </div>
            <div style={{ padding: "0.5rem", backgroundColor: "#1e293b", borderRadius: "0.25rem", display: "flex", justifyContent: "space-between" }}>
              <span>Max File Size</span>
              <span style={{ fontWeight: "bold", color: "#38bdf8" }}>10 MB</span>
            </div>
            <div style={{ padding: "0.5rem", backgroundColor: "#1e293b", borderRadius: "0.25rem", display: "flex", justifyContent: "space-between" }}>
              <span>Max Mission Timeout</span>
              <span style={{ fontWeight: "bold", color: "#38bdf8" }}>600s</span>
            </div>
            <div style={{ padding: "0.5rem", backgroundColor: "#1e293b", borderRadius: "0.25rem", display: "flex", justifyContent: "space-between" }}>
              <span>Max Concurrent Tasks</span>
              <span style={{ fontWeight: "bold", color: "#38bdf8" }}>3</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
