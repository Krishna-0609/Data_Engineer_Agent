"use client";

import { useEffect, useState } from "react";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { FolderGit2, Plus, ArrowRight, X, Calendar, Layers } from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { formatDate } from "@/lib/utils";
import Link from "next/link";

export default function ProjectsPage() {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [creating, setCreating] = useState(false);

  async function fetchProjects() {
    try {
      const res = await apiClient.get("/projects/");
      setProjects(res.data.items || []);
    } catch (err) {
      console.error("Fetch projects error:", err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setCreating(true);

    try {
      await apiClient.post("/projects/", { name, description });
      setName("");
      setDescription("");
      setShowModal(false);
      fetchProjects();
    } catch (err) {
      alert("Failed to create project.");
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-[#0B0F19]">
      <Sidebar />

      <div className="flex-1 flex flex-col min-w-0">
        <Header />

        <main className="p-8 space-y-8 flex-1">
          {/* Header Bar */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">Data Engineering Projects</h1>
              <p className="text-sm text-gray-400 mt-1">
                Manage your enterprise data workspaces, pipelines, and schema architectures.
              </p>
            </div>

            <button
              onClick={() => setShowModal(true)}
              className="gradient-button text-white text-xs font-semibold px-4 py-2.5 rounded-lg flex items-center gap-2 shadow-md shadow-indigo-500/20"
            >
              <Plus className="w-4 h-4" />
              New Project
            </button>
          </div>

          {/* Projects Grid */}
          {loading ? (
            <div className="py-16 text-center text-xs text-gray-500">Loading projects...</div>
          ) : projects.length === 0 ? (
            <div className="py-20 text-center glass-card rounded-2xl border border-dashed border-white/10">
              <FolderGit2 className="w-12 h-12 text-indigo-400/50 mx-auto mb-3" />
              <h3 className="text-base font-semibold text-white">No Projects Found</h3>
              <p className="text-xs text-gray-400 mt-1 max-w-sm mx-auto">
                Create a project to organize your ETL pipelines, data source connections, and execution schedules.
              </p>
              <button
                onClick={() => setShowModal(true)}
                className="mt-5 gradient-button text-white text-xs font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                Create First Project
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {projects.map((proj) => (
                <div
                  key={proj.id}
                  className="glass-card glass-card-hover rounded-xl p-6 border border-white/10 flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
                        <FolderGit2 className="w-5 h-5" />
                      </div>
                      <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 uppercase">
                        {proj.status}
                      </span>
                    </div>

                    <h3 className="text-base font-semibold text-white tracking-tight">{proj.name}</h3>
                    <p className="text-xs text-gray-400 mt-1.5 line-clamp-2">
                      {proj.description || "No description provided."}
                    </p>
                  </div>

                  <div className="mt-6 pt-4 border-t border-white/5 flex items-center justify-between text-xs text-gray-400">
                    <span className="flex items-center gap-1.5">
                      <Calendar className="w-3.5 h-3.5" />
                      {formatDate(proj.created_at)}
                    </span>

                    <Link
                      href={`/pipelines`}
                      className="text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1"
                    >
                      Pipelines <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>

      {/* Create Project Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg bg-slate-900 border border-white/10 rounded-2xl p-6 shadow-2xl relative">
            <div className="flex items-center justify-between pb-4 border-b border-white/10">
              <h3 className="text-lg font-bold text-white">Create New Data Project</h3>
              <button
                onClick={() => setShowModal(false)}
                className="p-1 text-gray-400 hover:text-white rounded-lg hover:bg-white/5"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateProject} className="mt-6 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">
                  Project Name
                </label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. E-Commerce Customer Analytics"
                  className="w-full bg-slate-950/80 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500/60"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">
                  Description
                </label>
                <textarea
                  rows={3}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Describe the scope, datasets, and target architecture..."
                  className="w-full bg-slate-950/80 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500/60"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-white/10">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-xs font-semibold text-gray-400 hover:text-white rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="gradient-button text-white text-xs font-semibold px-5 py-2 rounded-lg shadow-md shadow-indigo-500/20 disabled:opacity-50"
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
