"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import React, { useCallback, useEffect, useRef, useState } from "react";
import {
  API_BASE,
  AuthUser,
  authHeaders,
  clearAuth,
  getStoredToken,
  getStoredUser,
  parseApiError,
} from "@/lib/api";

interface ResearchProject {
  id: string;
  name: string;
  description: string;
  document_count: number;
  note_count: number;
  last_session_at?: string;
}

interface ResearchDocument {
  id: string;
  filename: string;
  summary: string;
  page_count: number;
  char_count: number;
  uploaded_at: string;
}

interface ResearchNote {
  id: string;
  title: string;
  body: string;
  tags: string[];
  document_id?: string;
  updated_at: string;
}

interface ResearchMessage {
  id: string;
  role: string;
  content: string;
  sources: string[];
  created_at: string;
}

interface ResearchConversation {
  id: string;
  title: string;
  message_count: number;
  updated_at: string;
}

interface SearchResult {
  result_type: string;
  id: string;
  title: string;
  snippet: string;
}

interface ProjectDetail {
  project: ResearchProject;
  documents: ResearchDocument[];
  notes: ResearchNote[];
  session?: {
    active_document_id?: string;
    active_conversation_id?: string;
    last_active_at: string;
  };
  conversations: ResearchConversation[];
  active_conversation?: {
    conversation: ResearchConversation;
    messages: ResearchMessage[];
  };
}

export default function ResearchPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<AuthUser | null>(null);
  const [authChecked, setAuthChecked] = useState(false);
  const [projects, setProjects] = useState<ResearchProject[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<ProjectDetail | null>(null);
  const [newProjectName, setNewProjectName] = useState("");
  const [newProjectDesc, setNewProjectDesc] = useState("");
  const [editProjectName, setEditProjectName] = useState("");
  const [editProjectDesc, setEditProjectDesc] = useState("");
  const [noteTitle, setNoteTitle] = useState("");
  const [noteBody, setNoteBody] = useState("");
  const [noteTags, setNoteTags] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[] | null>(null);
  const [searchLoading, setSearchLoading] = useState(false);
  const [chatQuestion, setChatQuestion] = useState("");
  const [selectedDocId, setSelectedDocId] = useState<string>("");
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const statusTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const showStatus = useCallback((message: string) => {
    setStatus(message);
    if (statusTimer.current) clearTimeout(statusTimer.current);
    statusTimer.current = setTimeout(() => setStatus(null), 6000);
  }, []);

  const handleUnauthorized = useCallback(() => {
    clearAuth();
    router.replace("/login");
  }, [router]);

  const apiFetch = useCallback(
    async (path: string, init?: RequestInit) => {
      if (!token) throw new Error("Not authenticated");
      const res = await fetch(`${API_BASE}${path}`, {
        ...init,
        headers: { ...authHeaders(token), ...(init?.headers || {}) },
      });
      if (res.status === 401) {
        handleUnauthorized();
        throw new Error("Session expired. Please sign in again.");
      }
      return res;
    },
    [token, handleUnauthorized]
  );

  useEffect(() => {
    const stored = getStoredToken();
    if (!stored) {
      router.replace("/login");
      return;
    }
    setToken(stored);
    setUser(getStoredUser());
    setAuthChecked(true);
  }, [router]);

  const loadProjects = useCallback(async () => {
    if (!token) return;
    try {
      const res = await apiFetch("/research/projects");
      if (!res.ok) throw new Error(await parseApiError(res));
      setProjects(await res.json());
    } catch (e) {
      showStatus(`Failed to load projects: ${e instanceof Error ? e.message : e}`);
    }
  }, [token, apiFetch, showStatus]);

  const loadProject = useCallback(
    async (projectId: string) => {
      if (!token) return;
      setLoading(true);
      try {
        await apiFetch(`/research/projects/${projectId}/sessions/resume`, { method: "POST" });
        const res = await apiFetch(`/research/projects/${projectId}`);
        if (!res.ok) throw new Error(await parseApiError(res));
        const data: ProjectDetail = await res.json();
        setDetail(data);
        setSelectedId(projectId);
        setEditProjectName(data.project.name);
        setEditProjectDesc(data.project.description);
        if (data.session?.active_document_id) {
          setSelectedDocId(data.session.active_document_id);
        }
        showStatus(`Resumed session for "${data.project.name}"`);
      } catch (e) {
        showStatus(`Failed to load project: ${e instanceof Error ? e.message : e}`);
      } finally {
        setLoading(false);
      }
    },
    [token, apiFetch, showStatus]
  );

  useEffect(() => {
    if (authChecked && token) loadProjects();
  }, [authChecked, token, loadProjects]);

  const logout = () => {
    clearAuth();
    router.replace("/login");
  };

  const createProject = async () => {
    if (!newProjectName.trim()) return;
    setLoading(true);
    try {
      const res = await apiFetch("/research/projects", {
        method: "POST",
        body: JSON.stringify({ name: newProjectName, description: newProjectDesc }),
      });
      if (!res.ok) throw new Error(await parseApiError(res));
      const project = await res.json();
      setNewProjectName("");
      setNewProjectDesc("");
      await loadProjects();
      await loadProject(project.id);
      showStatus(`Created project "${project.name}"`);
    } catch (e) {
      showStatus(`Create failed: ${e instanceof Error ? e.message : e}`);
    } finally {
      setLoading(false);
    }
  };

  const saveProject = async () => {
    if (!selectedId) return;
    setLoading(true);
    try {
      const res = await apiFetch(`/research/projects/${selectedId}`, {
        method: "PUT",
        body: JSON.stringify({ name: editProjectName, description: editProjectDesc }),
      });
      if (!res.ok) throw new Error(await parseApiError(res));
      await loadProjects();
      await loadProject(selectedId);
      showStatus("Project updated");
    } catch (e) {
      showStatus(`Update failed: ${e instanceof Error ? e.message : e}`);
    } finally {
      setLoading(false);
    }
  };

  const uploadPdf = async (file: File) => {
    if (!selectedId || !token) return;
    setLoading(true);
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(
        `${API_BASE}/research/projects/${selectedId}/documents/upload`,
        {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
          body: form,
        }
      );
      if (res.status === 401) {
        handleUnauthorized();
        return;
      }
      if (!res.ok) throw new Error(await parseApiError(res));
      const doc = await res.json();
      await loadProject(selectedId);
      showStatus(
        `Uploaded ${file.name} — ${doc.char_count?.toLocaleString() ?? 0} characters extracted`
      );
    } catch (e) {
      showStatus(`Upload failed: ${e instanceof Error ? e.message : e}`);
    } finally {
      setLoading(false);
    }
  };

  const summarize = async (docId: string) => {
    if (!selectedId) return;
    setLoading(true);
    try {
      const res = await apiFetch(
        `/research/projects/${selectedId}/documents/${docId}/summarize`,
        { method: "POST" }
      );
      if (!res.ok) throw new Error(await parseApiError(res));
      await loadProject(selectedId);
      showStatus("Summary generated");
    } catch (e) {
      showStatus(`Summarize failed: ${e instanceof Error ? e.message : e}`);
    } finally {
      setLoading(false);
    }
  };

  const saveNote = async () => {
    if (!selectedId || !noteTitle.trim()) return;
    setLoading(true);
    try {
      const tags = noteTags.split(",").map((t) => t.trim()).filter(Boolean);
      const res = await apiFetch(`/research/projects/${selectedId}/notes`, {
        method: "POST",
        body: JSON.stringify({
          title: noteTitle,
          body: noteBody,
          tags,
          document_id: selectedDocId || undefined,
        }),
      });
      if (!res.ok) throw new Error(await parseApiError(res));
      setNoteTitle("");
      setNoteBody("");
      setNoteTags("");
      await loadProject(selectedId);
      showStatus("Note saved");
    } catch (e) {
      showStatus(`Note failed: ${e instanceof Error ? e.message : e}`);
    } finally {
      setLoading(false);
    }
  };

  const deleteNote = async (noteId: string) => {
    if (!selectedId) return;
    try {
      const res = await apiFetch(`/research/projects/${selectedId}/notes/${noteId}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error(await parseApiError(res));
      await loadProject(selectedId);
      showStatus("Note deleted");
    } catch (e) {
      showStatus(`Delete failed: ${e instanceof Error ? e.message : e}`);
    }
  };

  const askQuestion = async (conversationId?: string) => {
    if (!selectedId || !chatQuestion.trim()) return;
    setLoading(true);
    try {
      const res = await apiFetch(`/research/projects/${selectedId}/ask`, {
        method: "POST",
        body: JSON.stringify({
          question: chatQuestion,
          document_id: selectedDocId || undefined,
          conversation_id: conversationId,
        }),
      });
      if (!res.ok) throw new Error(await parseApiError(res));
      setChatQuestion("");
      await loadProject(selectedId);
      showStatus("Question answered");
    } catch (e) {
      showStatus(`Q&A failed: ${e instanceof Error ? e.message : e}`);
    } finally {
      setLoading(false);
    }
  };

  const loadConversation = async (conversationId: string) => {
    if (!selectedId) return;
    setLoading(true);
    try {
      const res = await apiFetch(
        `/research/projects/${selectedId}/conversations/${conversationId}`
      );
      if (!res.ok) throw new Error(await parseApiError(res));
      await loadProject(selectedId);
      showStatus("Conversation loaded");
    } catch (e) {
      showStatus(`Failed to load conversation: ${e instanceof Error ? e.message : e}`);
    } finally {
      setLoading(false);
    }
  };

  const runSearch = async () => {
    if (!searchQuery.trim()) return;
    setSearchLoading(true);
    setSearchResults(null);
    try {
      const params = new URLSearchParams({ q: searchQuery });
      if (selectedId) params.set("project_id", selectedId);
      const res = await apiFetch(`/research/search?${params}`);
      if (!res.ok) throw new Error(await parseApiError(res));
      setSearchResults(await res.json());
    } catch (e) {
      showStatus(`Search failed: ${e instanceof Error ? e.message : e}`);
      setSearchResults([]);
    } finally {
      setSearchLoading(false);
    }
  };

  if (!authChecked) {
    return (
      <div className="research-loading-screen" aria-live="polite">
        <p>Loading…</p>
        <style jsx>{`
          .research-loading-screen {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #0a0a0f;
            color: #8888a0;
          }
        `}</style>
      </div>
    );
  }

  const messages = detail?.active_conversation?.messages ?? [];

  return (
    <div className="research-app" aria-busy={loading}>
      {loading && (
        <div className="research-overlay" aria-hidden="true">
          <div className="research-spinner" />
        </div>
      )}

      <header className="research-header">
        <div>
          <Link href="/" className="research-back">
            ← AXIOM
          </Link>
          <h1>Research Workspace</h1>
          <p>Projects · PDFs · Notes · Q&amp;A · Search · Sessions</p>
        </div>
        <div className="research-user">
          <Link href="/research/runs" className="research-runs-link">
            Research Runs
          </Link>
          {user && (
            <span className="research-user-name" title={user.email}>
              {user.name}
            </span>
          )}
          <button type="button" className="research-logout" onClick={logout}>
            Sign out
          </button>
        </div>
      </header>

      {status && (
        <div className="research-status" role="status" aria-live="polite">
          {status}
          <button
            type="button"
            className="research-status-close"
            onClick={() => setStatus(null)}
            aria-label="Dismiss notification"
          >
            ×
          </button>
        </div>
      )}

      <div className="research-grid">
        <aside className="research-sidebar" aria-label="Projects sidebar">
          <h2>Projects</h2>
          <div className="research-new-project">
            <input
              placeholder="Project name"
              value={newProjectName}
              onChange={(e) => setNewProjectName(e.target.value)}
              aria-label="New project name"
              disabled={loading}
            />
            <textarea
              placeholder="Description (optional)"
              value={newProjectDesc}
              onChange={(e) => setNewProjectDesc(e.target.value)}
              rows={2}
              aria-label="New project description"
              disabled={loading}
            />
            <button type="button" onClick={createProject} disabled={loading || !newProjectName.trim()}>
              Create Project
            </button>
          </div>
          {projects.length === 0 ? (
            <p className="research-empty-sidebar">No projects yet. Create one to get started.</p>
          ) : (
            <ul className="research-project-list" role="list">
              {projects.map((p) => (
                <li key={p.id}>
                  <button
                    type="button"
                    className={selectedId === p.id ? "active" : ""}
                    onClick={() => loadProject(p.id)}
                    aria-current={selectedId === p.id ? "page" : undefined}
                  >
                    <strong>{p.name}</strong>
                    <span>
                      {p.document_count} docs · {p.note_count} notes
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </aside>

        <main className="research-main" id="main-content">
          {!detail ? (
            <div className="research-empty" role="status">
              <p>Select a project from the sidebar, or create a new one to begin your research.</p>
            </div>
          ) : (
            <>
              <section aria-labelledby="organize-heading">
                <h2 id="organize-heading">Organize Project</h2>
                <input
                  value={editProjectName}
                  onChange={(e) => setEditProjectName(e.target.value)}
                  placeholder="Project name"
                  aria-label="Project name"
                  disabled={loading}
                />
                <textarea
                  value={editProjectDesc}
                  onChange={(e) => setEditProjectDesc(e.target.value)}
                  placeholder="Description"
                  rows={2}
                  aria-label="Project description"
                  disabled={loading}
                />
                <button type="button" onClick={saveProject} disabled={loading}>
                  Save Project
                </button>
                {detail.session && (
                  <p className="research-meta">
                    Session active · last:{" "}
                    {new Date(detail.session.last_active_at).toLocaleString()}
                  </p>
                )}
              </section>

              <section aria-labelledby="upload-heading">
                <h3 id="upload-heading">Upload PDF</h3>
                <p className="research-muted">
                  PDF text is extracted automatically on upload. Scanned or image-only PDFs are not supported.
                </p>
                <input
                  type="file"
                  accept="application/pdf"
                  aria-label="Upload PDF file"
                  disabled={loading}
                  onChange={(e) => {
                    const f = e.target.files?.[0];
                    if (f) uploadPdf(f);
                    e.target.value = "";
                  }}
                />
              </section>

              <section aria-labelledby="docs-heading">
                <h3 id="docs-heading">Documents ({detail.documents.length})</h3>
                {detail.documents.length === 0 ? (
                  <p className="research-muted">No documents yet. Upload a PDF to extract text and enable Q&amp;A.</p>
                ) : (
                  <>
                    <select
                      value={selectedDocId}
                      onChange={(e) => setSelectedDocId(e.target.value)}
                      className="research-select"
                      aria-label="Document scope for Q&A"
                    >
                      <option value="">All documents (Q&amp;A scope)</option>
                      {detail.documents.map((doc) => (
                        <option key={doc.id} value={doc.id}>
                          {doc.filename}
                        </option>
                      ))}
                    </select>
                    {detail.documents.map((doc) => (
                      <article key={doc.id} className="research-card">
                        <header>
                          <strong>{doc.filename}</strong>
                          <span>
                            {doc.page_count} pages · {doc.char_count.toLocaleString()} chars extracted
                          </span>
                          <button type="button" onClick={() => summarize(doc.id)} disabled={loading}>
                            Generate Summary
                          </button>
                        </header>
                        {doc.summary ? (
                          <p className="research-summary">{doc.summary}</p>
                        ) : (
                          <p className="research-muted">No summary yet — click Generate Summary.</p>
                        )}
                      </article>
                    ))}
                  </>
                )}
              </section>

              <section aria-labelledby="qa-heading">
                <h3 id="qa-heading">Ask About Papers</h3>
                <div className="research-chat" role="log" aria-live="polite" aria-label="Q&A conversation">
                  {messages.length === 0 && (
                    <p className="research-muted">
                      Ask a question about your uploaded papers. Conversations are saved automatically.
                    </p>
                  )}
                  {messages.map((msg) => (
                    <div key={msg.id} className={`research-chat-msg research-chat-${msg.role}`}>
                      <strong>{msg.role === "user" ? "You" : "AXIOM"}</strong>
                      <p>{msg.content}</p>
                      {msg.sources?.length > 0 && (
                        <small>Sources: {msg.sources.join(", ")}</small>
                      )}
                    </div>
                  ))}
                </div>
                <textarea
                  placeholder="What does this paper say about the critical line?"
                  value={chatQuestion}
                  onChange={(e) => setChatQuestion(e.target.value)}
                  rows={3}
                  aria-label="Your question"
                  disabled={loading || detail.documents.length === 0}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      askQuestion(detail.session?.active_conversation_id);
                    }
                  }}
                />
                <button
                  type="button"
                  onClick={() => askQuestion(detail.session?.active_conversation_id)}
                  disabled={loading || !chatQuestion.trim() || detail.documents.length === 0}
                >
                  Ask
                </button>
                {detail.documents.length === 0 && (
                  <p className="research-muted">Upload a PDF before asking questions.</p>
                )}
                {detail.conversations.length > 0 && (
                  <div className="research-conversations">
                    <h4>Previous Conversations</h4>
                    <ul role="list">
                      {detail.conversations.map((c) => (
                        <li key={c.id}>
                          <button type="button" onClick={() => loadConversation(c.id)}>
                            {c.title} ({c.message_count} msgs)
                          </button>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </section>

              <section aria-labelledby="notes-heading">
                <h3 id="notes-heading">Structured Notes</h3>
                <input
                  placeholder="Note title"
                  value={noteTitle}
                  onChange={(e) => setNoteTitle(e.target.value)}
                  aria-label="Note title"
                  disabled={loading}
                />
                <input
                  placeholder="Tags (comma-separated)"
                  value={noteTags}
                  onChange={(e) => setNoteTags(e.target.value)}
                  aria-label="Note tags"
                  disabled={loading}
                />
                <textarea
                  placeholder="Note body — insights, questions, citations..."
                  value={noteBody}
                  onChange={(e) => setNoteBody(e.target.value)}
                  rows={4}
                  aria-label="Note body"
                  disabled={loading}
                />
                <button type="button" onClick={saveNote} disabled={loading || !noteTitle.trim()}>
                  Save Note
                </button>
                {detail.notes.length === 0 ? (
                  <p className="research-muted">No notes yet. Save insights as you read.</p>
                ) : (
                  <ul className="research-notes" role="list">
                    {detail.notes.map((note) => (
                      <li key={note.id}>
                        <strong>{note.title}</strong>
                        {note.tags.length > 0 && (
                          <span className="research-tags">
                            {note.tags.map((t) => (
                              <span key={t} className="research-tag">
                                {t}
                              </span>
                            ))}
                          </span>
                        )}
                        <p>{note.body}</p>
                        <div className="research-note-actions">
                          <small>{new Date(note.updated_at).toLocaleString()}</small>
                          <button type="button" onClick={() => deleteNote(note.id)}>
                            Delete
                          </button>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </section>

              <section aria-labelledby="search-heading">
                <h3 id="search-heading">Search Papers &amp; Notes</h3>
                <p className="research-muted">
                  Full-text search across uploaded PDFs and saved notes (keyword matching, not vector semantic search).
                </p>
                <div className="research-search">
                  <input
                    placeholder="Search across uploaded content..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && runSearch()}
                    aria-label="Search query"
                    disabled={searchLoading}
                  />
                  <button type="button" onClick={runSearch} disabled={searchLoading || !searchQuery.trim()}>
                    {searchLoading ? "Searching…" : "Search"}
                  </button>
                </div>
                {searchResults !== null && (
                  searchResults.length === 0 ? (
                    <p className="research-muted" role="status">No results found for &ldquo;{searchQuery}&rdquo;.</p>
                  ) : (
                    <ul className="research-search-results" role="list">
                      {searchResults.map((r) => (
                        <li key={`${r.result_type}-${r.id}`}>
                          <span className="research-badge">{r.result_type}</span>
                          <strong>{r.title}</strong>
                          <p>{r.snippet}</p>
                        </li>
                      ))}
                    </ul>
                  )
                )}
              </section>
            </>
          )}
        </main>
      </div>

      <style jsx>{`
        .research-app {
          min-height: 100vh;
          background: #0a0a0f;
          color: #e8e8ef;
          font-family: Inter, system-ui, sans-serif;
          position: relative;
        }
        .research-overlay {
          position: fixed;
          inset: 0;
          background: rgba(10, 10, 15, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 100;
        }
        .research-spinner {
          width: 36px;
          height: 36px;
          border: 3px solid #2a2a3a;
          border-top-color: #4f5dff;
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        .research-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          padding: 1.5rem 2rem;
          border-bottom: 1px solid #1e1e2e;
        }
        .research-back {
          color: #7c8cff;
          text-decoration: none;
          font-size: 0.85rem;
        }
        .research-header h1 {
          margin: 0.5rem 0 0.25rem;
          font-size: 1.75rem;
        }
        .research-header p {
          margin: 0;
          color: #8888a0;
          font-size: 0.9rem;
        }
        .research-user {
          display: flex;
          align-items: center;
          gap: 1rem;
        }
        .research-runs-link {
          color: #7c8cff;
          text-decoration: none;
          font-size: 0.85rem;
        }
        .research-user-name {
          font-size: 0.85rem;
          color: #b8b8d0;
        }
        .research-logout {
          background: transparent;
          border: 1px solid #2a2a3a;
          color: #8888a0;
          padding: 0.4rem 0.75rem;
          border-radius: 6px;
          cursor: pointer;
          font-size: 0.8rem;
        }
        .research-logout:hover {
          border-color: #4a4a5a;
          color: #e8e8ef;
        }
        .research-status {
          margin: 1rem 2rem;
          padding: 0.75rem 1rem;
          background: #12121a;
          border: 1px solid #2a2a3a;
          border-radius: 8px;
          font-size: 0.9rem;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        .research-status-close {
          background: none;
          border: none;
          color: #8888a0;
          cursor: pointer;
          font-size: 1.2rem;
          line-height: 1;
        }
        .research-grid {
          display: grid;
          grid-template-columns: 280px 1fr;
          gap: 0;
          min-height: calc(100vh - 120px);
        }
        @media (max-width: 768px) {
          .research-grid {
            grid-template-columns: 1fr;
          }
        }
        .research-sidebar {
          border-right: 1px solid #1e1e2e;
          padding: 1.5rem;
        }
        .research-sidebar h2 {
          font-size: 0.85rem;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          color: #8888a0;
          margin: 0 0 1rem;
        }
        .research-empty-sidebar {
          color: #666680;
          font-size: 0.85rem;
          margin-top: 1rem;
        }
        .research-new-project input,
        .research-new-project textarea,
        .research-main input,
        .research-main textarea,
        .research-select {
          width: 100%;
          margin-bottom: 0.5rem;
          background: #12121a;
          border: 1px solid #2a2a3a;
          color: #e8e8ef;
          padding: 0.5rem;
          border-radius: 6px;
          box-sizing: border-box;
        }
        .research-select {
          max-width: 400px;
        }
        .research-new-project button,
        .research-main button {
          background: #4f5dff;
          color: white;
          border: none;
          padding: 0.5rem 1rem;
          border-radius: 6px;
          cursor: pointer;
          font-size: 0.85rem;
          margin-right: 0.5rem;
        }
        .research-new-project button:disabled,
        .research-main button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        .research-project-list {
          list-style: none;
          padding: 0;
          margin: 1.5rem 0 0;
        }
        .research-project-list button {
          width: 100%;
          text-align: left;
          background: transparent;
          border: 1px solid transparent;
          color: #e8e8ef;
          padding: 0.75rem;
          border-radius: 8px;
          cursor: pointer;
          margin-bottom: 0.25rem;
        }
        .research-project-list button:hover,
        .research-project-list button.active {
          background: #12121a;
          border-color: #2a2a3a;
        }
        .research-project-list span {
          display: block;
          font-size: 0.75rem;
          color: #8888a0;
          margin-top: 0.25rem;
        }
        .research-main {
          padding: 1.5rem 2rem;
          overflow-y: auto;
        }
        .research-main section {
          margin-bottom: 2rem;
        }
        .research-main h2 {
          margin: 0 0 0.5rem;
        }
        .research-main h3 {
          font-size: 1rem;
          margin: 0 0 0.5rem;
          color: #b8b8d0;
        }
        .research-main h4 {
          font-size: 0.9rem;
          color: #8888a0;
          margin: 1rem 0 0.5rem;
        }
        .research-meta {
          font-size: 0.85rem;
          color: #7c8cff;
          margin-top: 0.5rem;
        }
        .research-card {
          background: #12121a;
          border: 1px solid #2a2a3a;
          border-radius: 8px;
          padding: 1rem;
          margin-bottom: 0.75rem;
        }
        .research-card header {
          display: flex;
          flex-wrap: wrap;
          gap: 0.75rem;
          align-items: center;
          margin-bottom: 0.75rem;
        }
        .research-card header span {
          font-size: 0.8rem;
          color: #8888a0;
        }
        .research-summary {
          font-size: 0.9rem;
          line-height: 1.6;
          color: #c8c8d8;
        }
        .research-muted {
          color: #666680;
          font-size: 0.85rem;
          margin: 0 0 0.75rem;
        }
        .research-chat {
          background: #12121a;
          border: 1px solid #2a2a3a;
          border-radius: 8px;
          padding: 1rem;
          margin-bottom: 0.75rem;
          max-height: 320px;
          overflow-y: auto;
        }
        .research-chat-msg {
          margin-bottom: 1rem;
        }
        .research-chat-msg p {
          margin: 0.35rem 0;
          line-height: 1.5;
          font-size: 0.9rem;
        }
        .research-chat-msg small {
          color: #8888a0;
          font-size: 0.75rem;
        }
        .research-chat-user strong {
          color: #9ca8ff;
        }
        .research-chat-assistant strong {
          color: #6ee7b7;
        }
        .research-conversations ul {
          list-style: none;
          padding: 0;
        }
        .research-conversations button {
          background: transparent;
          border: none;
          color: #7c8cff;
          cursor: pointer;
          padding: 0.25rem 0;
          font-size: 0.85rem;
          text-align: left;
        }
        .research-notes {
          list-style: none;
          padding: 0;
          margin-top: 1rem;
        }
        .research-notes li {
          background: #12121a;
          border: 1px solid #2a2a3a;
          border-radius: 8px;
          padding: 1rem;
          margin-bottom: 0.5rem;
        }
        .research-notes p {
          margin: 0.5rem 0;
          font-size: 0.9rem;
          line-height: 1.5;
        }
        .research-tags {
          margin-left: 0.5rem;
        }
        .research-tag {
          font-size: 0.7rem;
          background: #2a2a4a;
          color: #9ca8ff;
          padding: 0.1rem 0.4rem;
          border-radius: 4px;
          margin-right: 0.25rem;
        }
        .research-note-actions {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        .research-note-actions button {
          background: transparent;
          border: 1px solid #4a3030;
          color: #ff8a8a;
          padding: 0.25rem 0.5rem;
          font-size: 0.75rem;
        }
        .research-search {
          display: flex;
          gap: 0.5rem;
          max-width: 600px;
        }
        .research-search input {
          flex: 1;
          margin: 0;
        }
        .research-search-results {
          list-style: none;
          padding: 0;
          margin-top: 1rem;
        }
        .research-search-results li {
          padding: 0.75rem 0;
          border-bottom: 1px solid #1e1e2e;
        }
        .research-badge {
          font-size: 0.7rem;
          text-transform: uppercase;
          background: #2a2a4a;
          color: #9ca8ff;
          padding: 0.15rem 0.4rem;
          border-radius: 4px;
          margin-right: 0.5rem;
        }
        .research-empty {
          color: #8888a0;
          padding: 4rem 0;
          text-align: center;
        }
      `}</style>
    </div>
  );
}
