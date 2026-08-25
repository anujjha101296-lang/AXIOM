/**
 * AXIOM Typed API Client
 * Centralized REST client connecting the Next.js frontend to the real FastAPI backend.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const DEV_TOKEN = "axiom-dev-token";

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  loading: boolean;
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const headers = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${DEV_TOKEN}`,
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(errData.detail || `HTTP Error ${response.status}`);
  }

  return response.json();
}

export const axiomApi = {
  // Projects & Workspace
  getProjects: () => request<any>("/api/v1/projects"),
  createProject: (name: string, description: string) =>
    request<any>("/api/v1/projects", {
      method: "POST",
      body: JSON.stringify({ name, description }),
    }),

  // Research Missions (Phase 19 & 20)
  getMissions: (projectId: string) => request<any>(`/api/v1/missions/project/${projectId}`),
  createMission: (projectId: string, name: string, objective: string) =>
    request<any>("/api/v1/missions", {
      method: "POST",
      body: JSON.stringify({ project_id: projectId, name, objective }),
    }),
  startMission: (missionId: string) => request<any>(`/api/v1/missions/${missionId}/start`, { method: "POST" }),
  pauseMission: (missionId: string) => request<any>(`/api/v1/missions/${missionId}/pause`, { method: "POST" }),
  emergencyStopMission: (missionId: string) => request<any>(`/api/v1/missions/${missionId}/emergency-stop`, { method: "POST" }),

  // Control Plane (Phase 20)
  getAgentProfiles: () => request<any>("/api/v1/control-plane/agents"),
  getDomainEvents: () => request<any>("/api/v1/control-plane/events"),
  getWorkerNodes: () => request<any>("/api/v1/control-plane/workers"),

  // Challenge Harness & Benchmarks (Phase 18)
  getChallenges: () => request<any>("/api/v1/benchmarks/challenges"),
  evaluateChallenge: (challengeId: string, agentOutput: string, proofScript?: string, witness?: string) =>
    request<any>("/api/v1/benchmarks/evaluate", {
      method: "POST",
      body: JSON.stringify({
        challenge_id: challengeId,
        agent_output: agentOutput,
        proof_script: proofScript || "",
        counterexample_witness: witness || "",
      }),
    }),
  getEvaluationResults: () => request<any>("/api/v1/benchmarks/results"),

  // Formal Math (Phase 16)
  verifyProofScript: (statementId: string, script: string) =>
    request<any>("/api/v1/formal-math/verify-lean", {
      method: "POST",
      body: JSON.stringify({ statement_id: statementId, script }),
    }),

  // Private Alpha (v0.1)
  getAlphaSummary: () => request<any>("/api/v1/alpha/stats"),
  getAlphaUsers: () => request<any>("/api/v1/alpha/users"),
  inviteAlphaUser: (email: string) =>
    request<any>(`/api/v1/alpha/users/invite?email=${encodeURIComponent(email)}`, { method: "POST" }),
  updateAlphaUserStatus: (userId: string, status: string) =>
    request<any>(`/api/v1/alpha/users/${userId}/status?status=${status}`, { method: "POST" }),
  submitFeedback: (feedback: any) =>
    request<any>("/api/v1/alpha/feedback", {
      method: "POST",
      body: JSON.stringify(feedback),
    }),
};
