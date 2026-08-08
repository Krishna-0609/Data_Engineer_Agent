"use client";

import { useState, useEffect } from "react";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import {
  Bot,
  Sparkles,
  Play,
  CheckCircle2,
  Activity,
  FileCode,
  Layers,
  ArrowRight,
  RefreshCw,
  Sliders,
  Database,
  Cpu,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";

export default function StudioPage() {
  const [projects, setProjects] = useState<any[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [prompt, setPrompt] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedResult, setGeneratedResult] = useState<any>(null);

  // Template suggestions
  const templates = [
    {
      title: "ETL Transaction Filter & Aggregate",
      prompt: "Extract customer transactions CSV from filesystem, clean missing email fields, aggregate daily user spend totals, and load to Snowflake.",
    },
    {
      title: "S3 to QuickSight Analytics Sync",
      prompt: "Ingest sales records from AWS S3 bucket 'finance-raw', cast date columns, aggregate monthly revenue by country, and sync to AWS QuickSight SPICE dataset.",
    },
    {
      title: "RDS Postgres to Power BI Pipeline",
      prompt: "Extract user activity logs from PostgreSQL RDS, filter test user accounts, group by activity event type, and push to Power BI service workspace.",
    },
  ];

  useEffect(() => {
    async function loadProjects() {
      try {
        const res = await apiClient.get("/projects/");
        const data = res.data || {};
        setProjects(data.items || []);
        if (data.items && data.items.length > 0) {
          setSelectedProjectId(data.items[0].id);
        }
      } catch (err) {
        console.error("Failed to load projects", err);
      }
    }
    loadProjects();
  }, []);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || !selectedProjectId) return;

    setIsGenerating(true);
    setGeneratedResult(null);

    try {
      const res = await apiClient.post("/agent/generate", {
        project_id: selectedProjectId,
        prompt: prompt,
      });

      setGeneratedResult(res.data);
    } catch (err) {
      console.error("Pipeline generation failed", err);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-[#0B0F19] text-white">
      <Sidebar />

      <div className="flex-1 flex flex-col min-w-0">
        <Header />

        <main className="p-8 space-y-8 overflow-y-auto">
          {/* Header Banner */}
          <div className="glass-card rounded-2xl p-6 border border-indigo-500/30 bg-gradient-to-r from-indigo-950/40 via-purple-950/20 to-slate-950/60 flex items-center justify-between">
            <div className="space-y-1">
              <div className="flex items-center gap-2 text-indigo-400 text-xs font-semibold uppercase tracking-wider">
                <Bot className="w-4 h-4" />
                Autonomous AI Agent Workbench
              </div>
              <h1 className="text-2xl font-bold text-white">AI Data Engineer Studio</h1>
              <p className="text-xs text-gray-400 max-w-xl">
                Describe your desired data pipeline architecture in plain natural language. The AI Agent will automatically synthesize DAG topology, write optimized Python pandas transformations, and enforce data quality guardrails.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <div className="text-right">
                <span className="text-[10px] text-gray-400 block uppercase">Target Project</span>
                <select
                  value={selectedProjectId}
                  onChange={(e) => setSelectedProjectId(e.target.value)}
                  className="bg-slate-950 text-xs text-white px-3 py-2 rounded-xl border border-indigo-500/30 focus:outline-none"
                >
                  {projects.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Quick Prompts & Prompt Input */}
          <div className="space-y-4">
            <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider">Quick Generator Templates</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {templates.map((tpl, i) => (
                <button
                  key={i}
                  onClick={() => setPrompt(tpl.prompt)}
                  className="p-4 rounded-xl glass-card border border-white/10 hover:border-indigo-500/40 text-left transition-all space-y-2 group"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-indigo-300 group-hover:text-indigo-200">{tpl.title}</span>
                    <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                  </div>
                  <p className="text-[11px] text-gray-400 line-clamp-2">{tpl.prompt}</p>
                </button>
              ))}
            </div>

            <form onSubmit={handleGenerate} className="glass-card rounded-2xl p-4 border border-indigo-500/30 space-y-4">
              <div className="relative">
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Describe your ETL pipeline requirement... e.g. Ingest customer CSV from S3, clean null email rows, calculate monthly user spend, and load to Snowflake."
                  rows={4}
                  className="w-full bg-slate-950/80 text-sm text-white placeholder-gray-500 rounded-xl p-4 border border-white/10 focus:outline-none focus:border-indigo-500/60"
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4 text-xs text-gray-400">
                  <span className="flex items-center gap-1.5"><Cpu className="w-3.5 h-3.5 text-indigo-400" /> LLM DAG Planner</span>
                  <span className="flex items-center gap-1.5"><Database className="w-3.5 h-3.5 text-emerald-400" /> Multi-Source Binding</span>
                </div>

                <button
                  type="submit"
                  disabled={isGenerating || !prompt.trim()}
                  className="gradient-button text-white text-xs font-semibold px-6 py-3 rounded-xl flex items-center gap-2 shadow-lg shadow-indigo-500/20 disabled:opacity-50"
                >
                  {isGenerating ? "Synthesizing Pipeline with AI..." : "Synthesize Pipeline Spec"}
                  <Sparkles className="w-4 h-4" />
                </button>
              </div>
            </form>
          </div>

          {/* AI Generation Stream & Result Visualizer */}
          {isGenerating && (
            <div className="glass-card rounded-2xl p-8 border border-indigo-500/30 text-center space-y-4">
              <div className="w-12 h-12 rounded-2xl bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center mx-auto animate-spin">
                <RefreshCw className="w-6 h-6 text-indigo-400" />
              </div>
              <div className="space-y-1">
                <h4 className="text-sm font-bold text-white">AI Data Engineer Agent Active</h4>
                <p className="text-xs text-gray-400">Analyzing prompt semantics → Constructing DAG topology nodes → Generating Python code...</p>
              </div>
            </div>
          )}

          {generatedResult && (
            <div className="glass-card rounded-2xl p-6 border border-emerald-500/30 bg-emerald-950/10 space-y-6">
              <div className="flex items-center justify-between border-b border-white/10 pb-4">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center">
                    <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-white">{generatedResult.name}</h3>
                    <p className="text-xs text-gray-400">{generatedResult.description}</p>
                  </div>
                </div>

                <a
                  href="/pipelines"
                  className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-4 py-2 rounded-xl flex items-center gap-1.5 transition-all shadow-md"
                >
                  View in Pipelines Workbench
                  <ArrowRight className="w-4 h-4" />
                </a>
              </div>

              {/* Generated Nodes Grid */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider">Synthesized DAG Nodes ({generatedResult.spec?.nodes?.length || 0})</h4>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  {generatedResult.spec?.nodes?.map((node: any, idx: number) => (
                    <div key={idx} className="p-4 rounded-xl bg-slate-950/80 border border-indigo-500/20 space-y-2">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-mono text-indigo-400 font-bold">Node {idx + 1}</span>
                        <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300">
                          {node.type}
                        </span>
                      </div>
                      <h5 className="text-xs font-bold text-white">{node.label || node.name || node.id}</h5>
                    </div>
                  ))}
                </div>
              </div>

              {/* Generated Python & SQL Code Inspector */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider">Synthesized Python Script</h4>
                  <pre className="rounded-xl bg-slate-950 p-4 font-mono text-xs text-indigo-300 border border-indigo-500/20 overflow-x-auto max-h-64">
                    {generatedResult.spec?.code?.python || generatedResult.spec?.python_code || "# Python transformation code synthesized automatically."}
                  </pre>
                </div>
                <div className="space-y-2">
                  <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider">Synthesized SQL Query</h4>
                  <pre className="rounded-xl bg-slate-950 p-4 font-mono text-xs text-purple-300 border border-purple-500/20 overflow-x-auto max-h-64">
                    {generatedResult.spec?.code?.sql || "-- SQL transformation query synthesized automatically."}
                  </pre>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
