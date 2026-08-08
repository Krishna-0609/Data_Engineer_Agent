"use client";

import { useEffect, useState } from "react";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import {
  FolderGit2,
  GitFork,
  CheckCircle2,
  Bot,
  Sparkles,
  ArrowUpRight,
  Play,
  Clock,
  Plus,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { formatDate } from "@/lib/utils";
import Link from "next/link";

export default function DashboardPage() {
  const [projects, setProjects] = useState<any[]>([]);
  const [pipelines, setPipelines] = useState<any[]>([]);
  const [prompt, setPrompt] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const projRes = await apiClient.get("/projects/");
        setProjects(projRes.data.items || []);

        if (projRes.data.items.length > 0) {
          const firstProjId = projRes.data.items[0].id;
          const pipeRes = await apiClient.get(`/pipelines/?project_id=${firstProjId}`);
          setPipelines(pipeRes.data.items || []);
        }
      } catch (err) {
        console.error("Dashboard fetch error:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const handlePromptSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    if (projects.length === 0) {
      alert("Please create a project first before generating pipelines.");
      return;
    }
    setIsGenerating(true);

    try {
      await apiClient.post("/agent/generate", {
        project_id: projects[0].id,
        prompt: prompt.trim(),
      });
      setPrompt("");
      window.location.href = "/pipelines";
    } catch (err: any) {
      console.error("AI Generation error:", err);
      alert(err.response?.data?.detail || "Failed to generate pipeline from AI Agent prompt.");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-[#0B0F19]">
      <Sidebar />

      <div className="flex-1 flex flex-col min-w-0">
        <Header />

        <main className="p-8 space-y-8 flex-1">
          {/* Welcome Banner */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">
                Enterprise AI Control Center
              </h1>
              <p className="text-sm text-gray-400 mt-1">
                Monitor autonomous pipeline execution and issue natural language agent prompts.
              </p>
            </div>
            <div className="flex items-center gap-3">
              <Link
                href="/projects"
                className="gradient-button text-white text-xs font-semibold px-4 py-2.5 rounded-lg flex items-center gap-2 shadow-md shadow-indigo-500/20"
              >
                <Plus className="w-4 h-4" />
                New Project
              </Link>
            </div>
          </div>

          {/* AI Prompt Launcher */}
          <div className="glass-card rounded-2xl p-6 border border-indigo-500/20 bg-gradient-to-r from-indigo-950/30 via-slate-900/60 to-purple-950/30 shadow-xl relative overflow-hidden">
            <div className="absolute -right-10 -bottom-10 w-48 h-48 bg-indigo-500/10 rounded-full blur-2xl pointer-events-none" />
            <div className="flex items-center gap-2 text-indigo-400 text-xs font-semibold tracking-wider uppercase mb-2">
              <Sparkles className="w-4 h-4" />
              AI Agent Pipeline Generator
            </div>
            <h2 className="text-lg font-semibold text-white mb-4">
              What pipeline would you like the AI Agent to build today?
            </h2>

            <form onSubmit={handlePromptSubmit} className="flex items-center gap-3">
              <div className="relative flex-1">
                <Bot className="w-5 h-5 text-gray-400 absolute left-4 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="e.g. Load customer orders from PostgreSQL every night, remove duplicates, calculate lifetime value, store in Delta Lake."
                  className="w-full bg-slate-950/80 text-sm text-white placeholder-gray-500 rounded-xl pl-12 pr-4 py-3 border border-white/10 focus:outline-none focus:border-indigo-500/60 transition-all"
                />
              </div>
              <button
                type="submit"
                disabled={isGenerating}
                className="gradient-button text-white text-sm font-semibold px-6 py-3 rounded-xl flex items-center gap-2 shrink-0 shadow-lg shadow-indigo-500/20 disabled:opacity-50"
              >
                {isGenerating ? "Generating Plan..." : "Generate Pipeline"}
                <Sparkles className="w-4 h-4" />
              </button>
            </form>
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
            <div className="glass-card glass-card-hover p-5 rounded-xl border border-white/10">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-gray-400">Total Projects</span>
                <FolderGit2 className="w-4 h-4 text-indigo-400" />
              </div>
              <p className="text-2xl font-bold text-white mt-3">{projects.length}</p>
              <div className="flex items-center gap-1 text-[11px] text-emerald-400 mt-1">
                <ArrowUpRight className="w-3 h-3" />
                <span>Active Workspace</span>
              </div>
            </div>

            <div className="glass-card glass-card-hover p-5 rounded-xl border border-white/10">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-gray-400">Total Pipelines</span>
                <GitFork className="w-4 h-4 text-purple-400" />
              </div>
              <p className="text-2xl font-bold text-white mt-3">{pipelines.length}</p>
              <div className="flex items-center gap-1 text-[11px] text-purple-400 mt-1">
                <span>Configured Jobs</span>
              </div>
            </div>

            <div className="glass-card glass-card-hover p-5 rounded-xl border border-white/10">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-gray-400">Pipeline Success Rate</span>
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              </div>
              <p className="text-2xl font-bold text-white mt-3">99.4%</p>
              <div className="flex items-center gap-1 text-[11px] text-emerald-400 mt-1">
                <span>Production SLA</span>
              </div>
            </div>

            <div className="glass-card glass-card-hover p-5 rounded-xl border border-white/10">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-gray-400">AI Prompt Operations</span>
                <Bot className="w-4 h-4 text-amber-400" />
              </div>
              <p className="text-2xl font-bold text-white mt-3">128</p>
              <div className="flex items-center gap-1 text-[11px] text-amber-400 mt-1">
                <span>Queries Processed</span>
              </div>
            </div>
          </div>

          {/* Pipelines Feed */}
          <div className="glass-card rounded-xl p-6 border border-white/10">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-base font-semibold text-white">Active Data Pipelines</h3>
                <p className="text-xs text-gray-400">Real-time status of configured pipeline specifications</p>
              </div>
              <Link href="/pipelines" className="text-xs text-indigo-400 hover:text-indigo-300 font-medium">
                View All →
              </Link>
            </div>

            {loading ? (
              <div className="py-8 text-center text-xs text-gray-500">Loading pipeline statistics...</div>
            ) : pipelines.length === 0 ? (
              <div className="py-12 text-center border border-dashed border-white/10 rounded-xl">
                <GitFork className="w-8 h-8 text-gray-600 mx-auto mb-2" />
                <p className="text-sm font-medium text-gray-300">No pipelines created yet</p>
                <p className="text-xs text-gray-500 mt-1">Use the AI Generator above or create one manually.</p>
              </div>
            ) : (
              <div className="divide-y divide-white/5">
                {pipelines.map((pipe) => (
                  <div key={pipe.id} className="py-4 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
                        <GitFork className="w-5 h-5" />
                      </div>
                      <div>
                        <h4 className="text-sm font-semibold text-white">{pipe.name}</h4>
                        <p className="text-xs text-gray-400">{pipe.description || "No description provided."}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-6">
                      <span className="text-xs text-gray-400 flex items-center gap-1.5">
                        <Clock className="w-3.5 h-3.5" />
                        {formatDate(pipe.created_at)}
                      </span>

                      <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-amber-500/10 border border-amber-500/20 text-amber-300 uppercase">
                        {pipe.status}
                      </span>

                      <button className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white transition-all">
                        <Play className="w-4 h-4 fill-current text-indigo-400" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
