"use client";

import React, { useCallback, useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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

interface Citation {
  document_id: string;
  filename: string;
  snippet: string;
  claim: string;
  evidence_mode: string;
}

interface AskResult {
  answer: string;
  conversation_id: string;
  message_id: string;
  sources: string[];
  citations: Citation[];
  provider_mode: string;
  uncertainty: string;
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
  const [token, setToken] = useState("axiom-dev-token");
  const [projects, setProjects] = useState<ResearchProject[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<ProjectDetail | null>(null);
  const [lastAsk, setLastAsk] = useState<AskResult | null>(null);
  const [newProjectName, setNewProjectName] = useState("");
  const [newProjectDesc, setNewProjectDesc] = useState("");
  const [editProjectName, setEditProjectName] = useState("");
  const [editProjectDesc, setEditProjectDesc] = useState("");
  const [noteTitle, setNoteTitle] = useState("");
  const [noteBody, setNoteBody] = useState("");
  const [noteTags, setNoteTags] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [chatQuestion, setChatQuestion] = useState("");
  const [selectedDocId, setSelectedDocId] = useState<string>("");
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

  const loadProjects = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/research/projects`, { headers: headers() });
      if (!res.ok) throw new Error(await res.text());
      setProjects(await res.json());
    } catch (e) {
      setStatus(`Failed to load projects: ${e}`);
    }
  }, [headers]);

  const loadProject = useCallback(
    async (projectId: string) => {
      setLoading(true);
      try {
        await fetch(`${API_BASE}/research/projects/${projectId}/sessions/resume`, {
          method: "POST",
          headers: headers(),
        });
        const res = await fetch(`${API_BASE}/research/projects/${projectId}`, {
          headers: headers(),
        });
        if (!res.ok) throw new Error(await res.text());
        const data: ProjectDetail = await res.json();
        setDetail(data);
        setSelectedId(projectId);
        setEditProjectName(data.project.name);
        setEditProjectDesc(data.project.description);
        setStatus(`Resumed session for "${data.project.name}"`);
      } catch (e) {
        setStatus(`Failed to load project: ${e}`);
      } finally {
        setLoading(false);
      }
    },
    [headers]
  );

  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  const createProject = async () => {
    if (!newProjectName.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/research/projects`, {
        method: "POST",
        headers: headers(),
        body: JSON.stringify({ name: newProjectName, description: newProjectDesc }),
      });
      if (!res.ok) throw new Error(await res.text());
      const project = await res.json();
      setNewProjectName("");
      setNewProjectDesc("");
      await loadProjects();
      await loadProject(project.id);
      setStatus(`Created project "${project.name}"`);
    } catch (e) {
      setStatus(`Create failed: ${e}`);
    } finally {
      setLoading(false);
    }
  };

  const saveProject = async () => {
    if (!selectedId) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/research/projects/${selectedId}`, {
        method: "PUT",
        headers: headers(),
        body: JSON.stringify({ name: editProjectName, description: editProjectDesc }),
      });
      if (!res.ok) throw new Error(await res.text());
      await loadProjects();
      await loadProject(selectedId);
      setStatus("Project updated");
    } catch (e) {
      setStatus(`Update failed: ${e}`);
    } finally {
      setLoading(false);
    }
  };

  const uploadPdf = async (file: File) => {
    if (!selectedId) return;
    setLoading(true);
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(`${API_BASE}/research/projects/${selectedId}/documents/upload`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: form,
      });
      if (!res.ok) throw new Error(await res.text());
      await loadProject(selectedId);
      setStatus(`Uploaded ${file.name}`);
    } catch (e) {
      setStatus(`Upload failed: ${e}`);
    } finally {
      setLoading(false);
    }
  };

  const summarize = async (docId: string) => {
    if (!selectedId) return;
    setLoading(true);
    try {
      const res = await fetch(
        `${API_BASE}/research/projects/${selectedId}/documents/${docId}/summarize`,
        { method: "POST", headers: headers() }
      );
      if (!res.ok) throw new Error(await res.text());
      await loadProject(selectedId);
      setStatus("Summary generated");
    } catch (e) {
      setStatus(`Summarize failed: ${e}`);
    } finally {
      setLoading(false);
    }
  };

  const saveNote = async () => {
    if (!selectedId || !noteTitle.trim()) return;
    setLoading(true);
    try {
      const tags = noteTags
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean);
      const res = await fetch(`${API_BASE}/research/projects/${selectedId}/notes`, {
        method: "POST",
        headers: headers(),
        body: JSON.stringify({
          title: noteTitle,
          body: noteBody,
          tags,
          document_id: selectedDocId || undefined,
        }),
      });
      if (!res.ok) throw new Error(await res.text());
      setNoteTitle("");
      setNoteBody("");
      setNoteTags("");
      await loadProject(selectedId);
      setStatus("Note saved");
    } catch (e) {
      setStatus(`Note failed: ${e}`);
    } finally {
      setLoading(false);
    }
  };

  const deleteNote = async (noteId: string) => {
    if (!selectedId) return;
    try {
      const res = await fetch(
        `${API_BASE}/research/projects/${selectedId}/notes/${noteId}`,
        { method: "DELETE", headers: headers() }
      );
      if (!res.ok) throw new Error(await res.text());
      await loadProject(selectedId);
      setStatus("Note deleted");
    } catch (e) {
      setStatus(`Delete failed: ${e}`);
    }
  };

  const askQuestion = async (conversationId?: string) => {
    if (!selectedId || !chatQuestion.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/research/projects/${selectedId}/ask`, {
        method: "POST",
        headers: headers(),
        body: JSON.stringify({
          question: chatQuestion,
          document_id: selectedDocId || undefined,
          conversation_id: conversationId,
        }),
      });
      if (!res.ok) throw new Error(await res.text());
      const askResult: AskResult = await res.json();
      setLastAsk(askResult);
      setChatQuestion("");
      await loadProject(selectedId);
      const mode = askResult.provider_mode || "unknown";
      setStatus(
        askResult.uncertainty
          ? `Answered (${mode}): ${askResult.uncertainty}`
          : `Question answered (${mode})`
      );
    } catch (e) {
      setStatus(`Q&A failed: ${e}`);
    } finally {
      setLoading(false);
    }
  };

  const loadConversation = async (conversationId: string) => {
    if (!selectedId) return;
    setLoading(true);
    try {
      const res = await fetch(
        `${API_BASE}/research/projects/${selectedId}/conversations/${conversationId}`,
        { headers: headers() }
      );
      if (!res.ok) throw new Error(await res.text());
      await loadProject(selectedId);
    } catch (e) {
      setStatus(`Failed to load conversation: ${e}`);
    } finally {
      setLoading(false);
    }
  };

  const runSearch = async () => {
    if (!searchQuery.trim()) return;
    try {
      const params = new URLSearchParams({ q: searchQuery });
      if (selectedId) params.set("project_id", selectedId);
      const res = await fetch(`${API_BASE}/research/search?${params}`, { headers: headers() });
      if (!res.ok) throw new Error(await res.text());
      setSearchResults(await res.json());
    } catch (e) {
      setStatus(`Search failed: ${e}`);
    }
  };

  const messages = detail?.active_conversation?.messages ?? [];

  return (
    <div className="research-app">
      <header className="research-header">
        <div>
          <a href="/" className="research-back">← AXIOM</a>
          <h1>Research Workspace</h1>
          <p>
            Projects · PDFs · Notes · Q&amp;A · Search ·{" "}
            <a href="/campaigns">Campaigns</a> · <a href="/experiments">Experiments</a> ·{" "}
            <a href="/sources">Sources</a> · <a href="/login">Sign in</a>
          </p>
        </div>
        <div className="research-token">
          <label htmlFor="api-token">API Token</label>
          <input
            id="api-token"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            type="password"
          />
          <button
            type="button"
            onClick={() => {
              try {
                localStorage.removeItem("axiom_access_token");
                localStorage.removeItem("axiom_user");
              } catch {
                /* ignore */
              }
              window.location.href = "/login";
            }}
          >
            Log out
          </button>
        </div>
      </header>

      {status && <div className="research-status">{status}</div>}

      <div className="research-grid">
        <aside className="research-sidebar">
          <h2>Projects</h2>
          <div className="research-new-project">
            <input
              placeholder="Project name"
              value={newProjectName}
              onChange={(e) => setNewProjectName(e.target.value)}
            />
            <textarea
              placeholder="Description (optional)"
              value={newProjectDesc}
              onChange={(e) => setNewProjectDesc(e.target.value)}
              rows={2}
            />
            <button type="button" onClick={createProject} disabled={loading}>
              Create Project
            </button>
          </div>
          <ul className="research-project-list">
            {projects.map((p) => (
              <li key={p.id}>
                <button
                  type="button"
                  className={selectedId === p.id ? "active" : ""}
                  onClick={() => loadProject(p.id)}
                >
                  <strong>{p.name}</strong>
                  <span>
                    {p.document_count} docs · {p.note_count} notes
                  </span>
                </button>
              </li>
            ))}
          </ul>
        </aside>

        <main className="research-main">
          {!detail ? (
            <div className="research-empty">
              <p>Create or select a research project to begin.</p>
            </div>
          ) : (
            <>
              <section>
                <h2>Organize Project</h2>
                <input
                  value={editProjectName}
                  onChange={(e) => setEditProjectName(e.target.value)}
                  placeholder="Project name"
                />
                <textarea
                  value={editProjectDesc}
                  onChange={(e) => setEditProjectDesc(e.target.value)}
                  placeholder="Description"
                  rows={2}
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

              <section>
                <h3>Upload PDF</h3>
                <input
                  type="file"
                  accept="application/pdf"
                  onChange={(e) => {
                    const f = e.target.files?.[0];
                    if (f) uploadPdf(f);
                  }}
                />
              </section>

              <section>
                <h3>Documents ({detail.documents.length})</h3>
                <select
                  value={selectedDocId}
                  onChange={(e) => setSelectedDocId(e.target.value)}
                  className="research-select"
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
                        {doc.page_count} pages · {doc.char_count.toLocaleString()} chars
                      </span>
                      <button type="button" onClick={() => summarize(doc.id)} disabled={loading}>
                        Generate Summary
                      </button>
                    </header>
                    {doc.summary ? (
                      <p className="research-summary">{doc.summary}</p>
                    ) : (
                      <p className="research-muted">No summary yet.</p>
                    )}
                  </article>
                ))}
              </section>

              <section>
                <h3>Ask About Papers</h3>
                <div className="research-chat">
                  {messages.length === 0 && (
                    <p className="research-muted">
                      Ask a question about your uploaded papers. Conversations are saved
                      automatically.
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
                {lastAsk && (
                  <div className="research-evidence" style={{ marginTop: 12 }}>
                    <p className="research-muted">
                      Provider: <strong>{lastAsk.provider_mode}</strong>
                      {lastAsk.uncertainty ? ` — ${lastAsk.uncertainty}` : ""}
                    </p>
                    {lastAsk.citations?.length > 0 && (
                      <ul className="research-notes">
                        {lastAsk.citations.map((c) => (
                          <li key={`${c.document_id}-${c.filename}`}>
                            <strong>{c.filename}</strong>
                            <span className="research-muted"> · {c.evidence_mode}</span>
                            {c.claim && <p>{c.claim}</p>}
                            {c.snippet && (
                              <small className="research-muted">{c.snippet.slice(0, 280)}</small>
                            )}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                )}
                <textarea
                  placeholder="What does this paper say about the critical line?"
                  value={chatQuestion}
                  onChange={(e) => setChatQuestion(e.target.value)}
                  rows={3}
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
                  disabled={loading || !chatQuestion.trim()}
                >
                  Ask
                </button>
                {detail.conversations.length > 0 && (
                  <div className="research-conversations">
                    <h4>Previous Conversations</h4>
                    <ul>
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

              <section>
                <h3>Structured Notes</h3>
                <input
                  placeholder="Note title"
                  value={noteTitle}
                  onChange={(e) => setNoteTitle(e.target.value)}
                />
                <input
                  placeholder="Tags (comma-separated)"
                  value={noteTags}
                  onChange={(e) => setNoteTags(e.target.value)}
                />
                <textarea
                  placeholder="Note body — insights, questions, citations..."
                  value={noteBody}
                  onChange={(e) => setNoteBody(e.target.value)}
                  rows={4}
                />
                <button type="button" onClick={saveNote} disabled={loading}>
                  Save Note
                </button>
                <ul className="research-notes">
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
              </section>

              <section>
                <h3>Search Papers &amp; Notes</h3>
                <div className="research-search">
                  <input
                    placeholder="Search across uploaded content..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && runSearch()}
                  />
                  <button type="button" onClick={runSearch}>
                    Search
                  </button>
                </div>
                <ul className="research-search-results">
                  {searchResults.map((r) => (
                    <li key={`${r.result_type}-${r.id}`}>
                      <span className="research-badge">{r.result_type}</span>
                      <strong>{r.title}</strong>
                      <p>{r.snippet}</p>
                    </li>
                  ))}
                </ul>
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
        .research-token label {
          display: block;
          font-size: 0.75rem;
          color: #8888a0;
          margin-bottom: 0.25rem;
        }
        .research-token input {
          background: #12121a;
          border: 1px solid #2a2a3a;
          color: #e8e8ef;
          padding: 0.5rem;
          border-radius: 6px;
          width: 200px;
        }
        .research-status {
          margin: 1rem 2rem;
          padding: 0.75rem 1rem;
          background: #12121a;
          border: 1px solid #2a2a3a;
          border-radius: 8px;
          font-size: 0.9rem;
        }
        .research-grid {
          display: grid;
          grid-template-columns: 280px 1fr;
          gap: 0;
          min-height: calc(100vh - 120px);
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
          margin: 0 0 1rem;
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
