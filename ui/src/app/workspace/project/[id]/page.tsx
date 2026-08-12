"use client";

import React, { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Project {
  id: string;
  name: string;
  description: string;
  owner_id: string;
}

interface Document {
  id: string;
  filename: string;
  created_at: string;
  status: string;
}

export default function ProjectPage() {
  const router = useRouter();
  const params = useParams();
  const projectId = params.id as string;

  const [project, setProject] = useState<Project | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);
  const [activeTab, setActiveTab] = useState<"overview" | "documents">("documents");

  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/");
      return;
    }

    const fetchData = async () => {
      try {
        // Fetch Project
        const projRes = await fetch(`${API_BASE}/projects/${projectId}`, {
          headers: { "Authorization": `Bearer ${token}` }
        });
        if (!projRes.ok) throw new Error("Failed to fetch project");
        const projData = await projRes.json();
        setProject(projData);

        // Fetch Documents
        const docsRes = await fetch(`${API_BASE}/projects/${projectId}/documents`, {
          headers: { "Authorization": `Bearer ${token}` }
        });
        if (!docsRes.ok) throw new Error("Failed to fetch documents");
        const docsData = await docsRes.json();
        setDocuments(docsData);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (projectId) {
      fetchData();
    }
  }, [projectId, router]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/");
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    setUploading(true);
    const token = localStorage.getItem("token");
    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const res = await fetch(`${API_BASE}/projects/${projectId}/documents`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`
        },
        body: formData
      });

      if (!res.ok) throw new Error("Failed to upload document");

      const newDoc = await res.json();
      setDocuments([newDoc, ...documents]);
      setSelectedFile(null);
      
      // Reset input file
      const fileInput = document.getElementById("file-upload") as HTMLInputElement;
      if (fileInput) fileInput.value = "";
    } catch (err: any) {
      alert(err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteDocument = async (docId: string) => {
    if (!confirm("Are you sure you want to delete this document?")) return;

    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`${API_BASE}/projects/${projectId}/documents/${docId}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` }
      });

      if (!res.ok) throw new Error("Failed to delete document");

      setDocuments(documents.filter(d => d.id !== docId));
    } catch (err: any) {
      alert(err.message);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-slate-950 text-white">
        <div className="animate-pulse">Loading project...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 font-sans text-slate-100 flex flex-col">
      {/* Top Navbar */}
      <header className="border-b border-slate-800 bg-slate-900 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-8">
          <Link href="/workspace" className="text-xl font-bold tracking-tight text-white flex items-center space-x-2">
            <span className="text-indigo-500">A</span>
            <span>AXIOM</span>
          </Link>
          <div className="text-slate-400 mx-2">/</div>
          <div className="font-medium text-white">{project?.name || "Project"}</div>
        </div>
        <div className="flex items-center space-x-4">
          <button 
            onClick={handleLogout}
            className="text-xs font-semibold px-3 py-1.5 rounded border border-slate-700 hover:bg-slate-800 transition-colors"
          >
            Sign Out
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 p-8 max-w-6xl mx-auto w-full">
        {error && <div className="bg-red-500/10 border border-red-500/50 text-red-400 p-4 rounded mb-6">{error}</div>}
        
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">{project?.name}</h1>
          <p className="text-slate-400">{project?.description || "No description provided."}</p>
        </div>

        {/* Tabs */}
        <div className="border-b border-slate-800 mb-6">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab("overview")}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === "overview"
                  ? "border-indigo-500 text-indigo-400"
                  : "border-transparent text-slate-400 hover:text-slate-300 hover:border-slate-700"
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab("documents")}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === "documents"
                  ? "border-indigo-500 text-indigo-400"
                  : "border-transparent text-slate-400 hover:text-slate-300 hover:border-slate-700"
              }`}
            >
              Documents
            </button>
          </nav>
        </div>

        {activeTab === "overview" && (
          <div className="py-12 text-center border border-dashed border-slate-700 rounded-lg bg-slate-900/50">
            <p className="text-slate-500">Project overview features coming soon.</p>
          </div>
        )}

        {activeTab === "documents" && (
          <div className="space-y-8">
            {/* Upload Section */}
            <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
              <h2 className="text-xl font-bold text-white mb-4">Upload Document</h2>
              <form onSubmit={handleUpload} className="flex items-end space-x-4">
                <div className="flex-1">
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Select PDF File</label>
                  <input
                    id="file-upload"
                    type="file"
                    accept="application/pdf"
                    onChange={handleFileChange}
                    className="block w-full text-sm text-slate-400
                      file:mr-4 file:py-2 file:px-4
                      file:rounded file:border-0
                      file:text-sm file:font-semibold
                      file:bg-indigo-900/50 file:text-indigo-300
                      hover:file:bg-indigo-900/80 file:cursor-pointer
                      border border-slate-800 rounded p-2 bg-slate-950"
                  />
                </div>
                <button
                  type="submit"
                  disabled={!selectedFile || uploading}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-2 px-6 rounded transition-colors disabled:opacity-50 h-[42px]"
                >
                  {uploading ? "Uploading..." : "Upload"}
                </button>
              </form>
            </div>

            {/* Document List */}
            <div>
              <h2 className="text-xl font-bold text-white mb-4">Project Documents</h2>
              {documents.length === 0 ? (
                <div className="py-12 text-center border border-dashed border-slate-700 rounded-lg bg-slate-900/50">
                  <p className="text-slate-500">No documents uploaded yet.</p>
                </div>
              ) : (
                <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden">
                  <table className="min-w-full divide-y divide-slate-800">
                    <thead className="bg-slate-950">
                      <tr>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Title / Filename</th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Status</th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Created</th>
                        <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800 bg-slate-900">
                      {documents.map((doc) => (
                        <tr key={doc.id}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-white">
                            {doc.filename || `Document ${doc.id.substring(0,8)}`}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                              ${doc.status === 'completed' ? 'bg-green-900/50 text-green-400' : 
                                doc.status === 'failed' ? 'bg-red-900/50 text-red-400' : 
                                'bg-yellow-900/50 text-yellow-400'}`}>
                              {doc.status || 'pending'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                            {new Date(doc.created_at).toLocaleString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <button
                              onClick={() => handleDeleteDocument(doc.id)}
                              className="text-red-400 hover:text-red-300"
                            >
                              Delete
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
