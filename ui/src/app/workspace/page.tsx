"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface User {
  id: string;
  email: string;
}

interface Project {
  id: string;
  name: string;
  description: string;
  owner_id: string;
}

export default function WorkspaceDashboard() {
  const router = useRouter();
  
  const [user, setUser] = useState<User | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newProjectName, setNewProjectName] = useState("");
  const [newProjectDesc, setNewProjectDesc] = useState("");
  const [creating, setCreating] = useState(false);

  const [activeTab, setActiveTab] = useState<"projects" | "documents" | "research">("projects");

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/");
      return;
    }

    const fetchDashboardData = async () => {
      try {
        // Fetch User
        const userRes = await fetch(`${API_BASE}/auth/me`, {
          headers: { "Authorization": `Bearer ${token}` }
        });
        if (!userRes.ok) {
          if (userRes.status === 401) {
            localStorage.removeItem("token");
            router.push("/");
            return;
          }
          throw new Error("Failed to fetch user");
        }
        const userData = await userRes.json();
        setUser(userData);

        // Fetch Projects
        const projRes = await fetch(`${API_BASE}/projects`, {
          headers: { "Authorization": `Bearer ${token}` }
        });
        if (!projRes.ok) throw new Error("Failed to fetch projects");
        
        const projData = await projRes.json();
        setProjects(projData);
        
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [router]);

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    const token = localStorage.getItem("token");
    
    try {
      const res = await fetch(`${API_BASE}/projects`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ name: newProjectName, description: newProjectDesc })
      });
      
      if (!res.ok) throw new Error("Failed to create project");
      
      const newProj = await res.json();
      setProjects([newProj, ...projects]);
      setShowCreateModal(false);
      setNewProjectName("");
      setNewProjectDesc("");
    } catch (err: any) {
      alert(err.message);
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteProject = async (id: string) => {
    if (!confirm("Are you sure you want to delete this project?")) return;
    
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`${API_BASE}/projects/${id}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` }
      });
      
      if (!res.ok) throw new Error("Failed to delete project");
      
      setProjects(projects.filter(p => p.id !== id));
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/");
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-slate-950 text-white">
        <div className="animate-pulse">Loading workspace...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 font-sans text-slate-100 flex flex-col">
      {/* ── Top Navbar ─────────────────────────────────────────────── */}
      <header className="border-b border-slate-800 bg-slate-900 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-8">
          <Link href="/" className="text-xl font-bold tracking-tight text-white flex items-center space-x-2">
            <span className="text-indigo-500">A</span>
            <span>AXIOM</span>
          </Link>
          <nav className="flex space-x-1">
            <button 
              onClick={() => setActiveTab("projects")}
              className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${activeTab === "projects" ? "bg-slate-800 text-white" : "text-slate-400 hover:text-slate-200"}`}
            >
              Projects
            </button>
            <button 
              onClick={() => setActiveTab("documents")}
              className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${activeTab === "documents" ? "bg-slate-800 text-white" : "text-slate-400 hover:text-slate-200"}`}
            >
              Documents
            </button>
            <button 
              onClick={() => setActiveTab("research")}
              className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${activeTab === "research" ? "bg-slate-800 text-white" : "text-slate-400 hover:text-slate-200"}`}
            >
              Research
            </button>
          </nav>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-slate-400">{user?.email}</div>
          <button 
            onClick={handleLogout}
            className="text-xs font-semibold px-3 py-1.5 rounded border border-slate-700 hover:bg-slate-800 transition-colors"
          >
            Sign Out
          </button>
        </div>
      </header>

      {/* ── Main Content ───────────────────────────────────────────── */}
      <main className="flex-1 p-8 max-w-6xl mx-auto w-full">
        {error && <div className="bg-red-500/10 border border-red-500/50 text-red-400 p-4 rounded mb-6">{error}</div>}
        
        {activeTab === "projects" && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-white mb-1">Your Projects</h1>
                <p className="text-sm text-slate-400">Manage your active research environments and workspaces.</p>
              </div>
              <button 
                onClick={() => setShowCreateModal(true)}
                className="bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-2 px-4 rounded transition-colors"
              >
                + New Project
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {projects.length === 0 ? (
                <div className="col-span-full py-12 text-center border border-dashed border-slate-700 rounded-lg">
                  <p className="text-slate-500 mb-4">You don't have any projects yet.</p>
                  <button 
                    onClick={() => setShowCreateModal(true)}
                    className="text-indigo-400 hover:text-indigo-300 font-medium"
                  >
                    Create your first project
                  </button>
                </div>
              ) : (
                projects.map(p => (
                  <div key={p.id} className="bg-slate-900 border border-slate-800 rounded-lg p-5 hover:border-slate-600 transition-colors flex flex-col group">
                    <h3 className="text-lg font-bold text-white mb-2 line-clamp-1">{p.name}</h3>
                    <p className="text-sm text-slate-400 flex-1 line-clamp-3 mb-4">{p.description || "No description provided."}</p>
                    <div className="flex items-center justify-between mt-auto pt-4 border-t border-slate-800/50">
                      <span className="text-xs text-slate-500 font-mono">ID: {p.id.substring(0, 8)}...</span>
                      <div className="space-x-2">
                        {/* Placeholder for opening actual graph workspace if we had one for specific projects */}
                        <button className="text-xs text-indigo-400 hover:text-indigo-300 font-medium">Open</button>
                        <button 
                          onClick={() => handleDeleteProject(p.id)}
                          className="text-xs text-slate-500 hover:text-red-400 font-medium transition-colors"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {activeTab === "documents" && (
          <div className="py-12 text-center border border-dashed border-slate-700 rounded-lg bg-slate-900/50">
            <h2 className="text-xl font-bold text-slate-300 mb-2">Documents</h2>
            <p className="text-slate-500">Not yet implemented. Check back later for document management features.</p>
          </div>
        )}

        {activeTab === "research" && (
          <div className="py-12 text-center border border-dashed border-slate-700 rounded-lg bg-slate-900/50">
            <h2 className="text-xl font-bold text-slate-300 mb-2">Research</h2>
            <p className="text-slate-500">Not yet implemented. Check back later for advanced research tracking features.</p>
          </div>
        )}
      </main>

      {/* ── Create Project Modal ───────────────────────────────────── */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-lg shadow-2xl w-full max-w-md">
            <h2 className="text-xl font-bold text-white mb-4">Create New Project</h2>
            <form onSubmit={handleCreateProject} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Project Name</label>
                <input 
                  type="text" 
                  value={newProjectName}
                  onChange={(e) => setNewProjectName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-white"
                  placeholder="e.g. Riemann Hypothesis Exploration"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Description (Optional)</label>
                <textarea 
                  value={newProjectDesc}
                  onChange={(e) => setNewProjectDesc(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-white min-h-[100px]"
                  placeholder="Briefly describe the research goals..."
                />
              </div>
              <div className="flex space-x-3 pt-2">
                <button 
                  type="button" 
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 bg-slate-800 hover:bg-slate-700 text-white font-medium py-2 rounded transition-colors"
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  disabled={creating || !newProjectName.trim()}
                  className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-2 rounded transition-colors disabled:opacity-50"
                >
                  {creating ? "Creating..." : "Create Project"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
