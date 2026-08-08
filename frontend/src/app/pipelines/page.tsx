"use client";

import { useEffect, useState } from "react";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import {
  GitFork,
  Play,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Layers,
  Code2,
  Database,
  Sparkles,
  Bot,
  Terminal,
  Activity,
  FileCode,
  Check,
  X,
  Download,
  Wind,
  RefreshCw,
  ShieldCheck,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { formatDate } from "@/lib/utils";

export default function PipelinesPage() {
  const [projects, setProjects] = useState<any[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [pipelines, setPipelines] = useState<any[]>([]);
  const [selectedPipeline, setSelectedPipeline] = useState<any>(null);

  // Execution state
  const [executing, setExecuting] = useState(false);
  const [lastExecution, setLastExecution] = useState<any>(null);

  // AI Generation Modal state
  const [isAiModalOpen, setIsAiModalOpen] = useState(false);
  const [aiPrompt, setAiPrompt] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);

  // Refinement state
  const [refinementPrompt, setRefinementPrompt] = useState("");
  const [isRefining, setIsRefining] = useState(false);

  // Airflow Export State
  const [airflowCode, setAirflowCode] = useState<string>("");
  const [loadingAirflow, setLoadingAirflow] = useState(false);

  // Tab state: 'dag' | 'code' | 'json' | 'logs' | 'airflow' | 'quality' | 'lineage'
  const [activeTab, setActiveTab] = useState<"dag" | "code" | "json" | "logs" | "airflow" | "quality" | "lineage">("dag");
  const [codeLang, setCodeLang] = useState<"python" | "sql">("python");

  useEffect(() => {
    async function init() {
      try {
        const projRes = await apiClient.get("/projects/");
        const projItems = projRes.data.items || [];
        setProjects(projItems);

        if (projItems.length > 0) {
          const pId = projItems[0].id;
          setSelectedProjectId(pId);
          await loadPipelines(pId);
        }
      } catch (err) {
        console.error("Pipeline init error:", err);
      }
    }
    init();
  }, []);

  async function loadPipelines(projectId: string) {
    try {
      const res = await apiClient.get(`/pipelines/?project_id=${projectId}`);
      const items = res.data.items || [];
      setPipelines(items);
      if (items.length > 0) {
        setSelectedPipeline(items[0]);
        loadExecutionHistory(items[0].id);
        loadAirflowExport(items[0].id);
      } else {
        setSelectedPipeline(null);
        setLastExecution(null);
        setAirflowCode("");
      }
    } catch (err) {
      console.error("Load pipelines error:", err);
    }
  }

  async function loadExecutionHistory(pipelineId: string) {
    try {
      const res = await apiClient.get(`/pipelines/${pipelineId}/history`);
      const items = res.data.items || [];
      if (items.length > 0) {
        setLastExecution(items[0]);
      } else {
        setLastExecution(null);
      }
    } catch (err) {
      console.error("Load execution history error:", err);
    }
  }

  async function loadAirflowExport(pipelineId: string) {
    setLoadingAirflow(true);
    try {
      const res = await apiClient.get(`/pipelines/${pipelineId}/export/airflow`);
      setAirflowCode(res.data);
    } catch (err) {
      setAirflowCode("# Failed to load Airflow DAG code.");
    } finally {
      setLoadingAirflow(false);
    }
  }

  const handleExecute = async () => {
    if (!selectedPipeline) return;
    setExecuting(true);
    try {
      const res = await apiClient.post(`/pipelines/${selectedPipeline.id}/execute`);
      setLastExecution(res.data);
      setActiveTab("logs");
    } catch (err) {
      alert("Failed to trigger pipeline execution.");
    } finally {
      setExecuting(false);
    }
  };

  const handleGenerateAi = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!aiPrompt.trim() || !selectedProjectId) return;
    setIsGenerating(true);

    try {
      const res = await apiClient.post("/agent/generate", {
        project_id: selectedProjectId,
        prompt: aiPrompt.trim(),
      });
      setIsAiModalOpen(false);
      setAiPrompt("");
      await loadPipelines(selectedProjectId);
      setSelectedPipeline(res.data);
      loadAirflowExport(res.data.id);
    } catch (err: any) {
      alert(err.response?.data?.detail || "AI Generation failed.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleRefinePipeline = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!refinementPrompt.trim() || !selectedPipeline) return;
    setIsRefining(true);

    try {
      const res = await apiClient.post("/agent/refine", {
        pipeline_id: selectedPipeline.id,
        refinement_prompt: refinementPrompt.trim(),
      });
      setSelectedPipeline(res.data);
      setRefinementPrompt("");
      await loadPipelines(selectedProjectId);
      loadAirflowExport(res.data.id);
      alert(`Pipeline specification refined to version v${res.data.version}!`);
    } catch (err: any) {
      alert(err.response?.data?.detail || "Pipeline refinement failed.");
    } finally {
      setIsRefining(false);
    }
  };

  const handleDownloadAirflow = () => {
    if (!selectedPipeline) return;
    const blob = new Blob([airflowCode], { type: "text/x-python" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `airflow_dag_${selectedPipeline.name.toLowerCase().replace(/\s+/g, "_")}.py`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const spec = selectedPipeline?.spec || {};
  const nodes = spec.nodes || [];
  const pythonCode = spec.code?.python || "# No Python code generated.";
  const sqlCode = spec.code?.sql || "-- No SQL query generated.";

  return (
    <div className="flex min-h-screen bg-[#0B0F19]">
      <Sidebar />

      <div className="flex-1 flex flex-col min-w-0">
        <Header />

        <main className="p-8 space-y-8 flex-1">
          {/* Top Control Bar */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">ETL / ELT Pipeline Workbench</h1>
              <p className="text-sm text-gray-400 mt-1">
                Inspect AI generated PySpark/SQL specs, export Apache Airflow DAGs, and execute runs.
              </p>
            </div>

            {/* Actions & Project Selector */}
            <div className="flex items-center gap-4">
              <button
                onClick={() => setIsAiModalOpen(true)}
                className="gradient-button text-white text-xs font-semibold px-4 py-2.5 rounded-xl flex items-center gap-2 shadow-lg shadow-indigo-500/20"
              >
                <Sparkles className="w-4 h-4" />
                Generate with AI Agent
              </button>

              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-gray-400">Project:</span>
                <select
                  value={selectedProjectId}
                  onChange={(e) => {
                    setSelectedProjectId(e.target.value);
                    loadPipelines(e.target.value);
                  }}
                  className="bg-slate-900 text-sm text-white border border-white/10 rounded-lg px-3 py-2 focus:outline-none focus:border-indigo-500"
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

          {/* Workbench Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Pipelines List Sidebar */}
            <div className="glass-card rounded-xl p-5 border border-white/10 space-y-4">
              <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4">
                Configured Pipelines ({pipelines.length})
              </h3>

              {pipelines.length === 0 ? (
                <div className="py-12 text-center text-xs text-gray-500">
                  No pipelines in this project yet. Click &quot;Generate with AI Agent&quot; above!
                </div>
              ) : (
                <div className="space-y-2">
                  {pipelines.map((pipe) => {
                    const isSelected = selectedPipeline?.id === pipe.id;
                    return (
                      <div
                        key={pipe.id}
                        onClick={() => {
                          setSelectedPipeline(pipe);
                          loadExecutionHistory(pipe.id);
                          loadAirflowExport(pipe.id);
                        }}
                        className={`p-4 rounded-xl cursor-pointer transition-all border ${
                          isSelected
                            ? "bg-indigo-600/20 border-indigo-500/50 shadow-md"
                            : "bg-white/5 border-transparent hover:bg-white/10"
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <h4 className="text-sm font-semibold text-white">{pipe.name}</h4>
                          <span className="text-[10px] px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 font-mono uppercase">
                            v{pipe.version}
                          </span>
                        </div>
                        <p className="text-xs text-gray-400 mt-1 line-clamp-1">{pipe.description}</p>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Spec & Execution Visualizer */}
            <div className="lg:col-span-2 space-y-6">
              {selectedPipeline ? (
                <>
                  {/* Selected Pipeline Header Card */}
                  <div className="glass-card rounded-xl p-6 border border-white/10 space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="flex items-center gap-3">
                          <h2 className="text-xl font-bold text-white">{selectedPipeline.name}</h2>
                          <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                            {selectedPipeline.status}
                          </span>
                          <span className="text-xs text-indigo-400 font-mono">
                            v{selectedPipeline.version}
                          </span>
                        </div>
                        <p className="text-xs text-gray-400 mt-1">{selectedPipeline.description}</p>
                      </div>

                      <div className="flex items-center gap-3">
                        <button
                          onClick={handleDownloadAirflow}
                          className="bg-slate-900 hover:bg-slate-800 text-cyan-300 border border-cyan-500/30 text-xs font-semibold px-4 py-2.5 rounded-xl flex items-center gap-2 transition-all shadow-md"
                        >
                          <Download className="w-3.5 h-3.5" />
                          Airflow DAG (.py)
                        </button>

                        <button
                          onClick={handleExecute}
                          disabled={executing}
                          className="gradient-button text-white text-xs font-semibold px-5 py-2.5 rounded-xl flex items-center gap-2 shadow-lg shadow-indigo-500/20 disabled:opacity-50"
                        >
                          <Play className="w-4 h-4 fill-current text-white" />
                          {executing ? "Running Execution Engine..." : "Execute Pipeline"}
                        </button>
                      </div>
                    </div>

                    {/* Interactive AI Refinement Bar */}
                    <form onSubmit={handleRefinePipeline} className="flex items-center gap-2 pt-2 border-t border-white/5">
                      <div className="relative flex-1">
                        <RefreshCw className="w-3.5 h-3.5 text-indigo-400 absolute left-3 top-1/2 -translate-y-1/2" />
                        <input
                          type="text"
                          value={refinementPrompt}
                          onChange={(e) => setRefinementPrompt(e.target.value)}
                          placeholder="Refine spec with AI (e.g. 'Add data quality check for null email values', 'Change schedule to hourly')"
                          className="w-full bg-slate-950/90 text-xs text-white placeholder-gray-500 rounded-lg pl-9 pr-3 py-2 border border-white/10 focus:outline-none focus:border-indigo-500/60"
                        />
                      </div>
                      <button
                        type="submit"
                        disabled={isRefining}
                        className="bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-300 text-xs font-semibold px-4 py-2 rounded-lg border border-indigo-500/40 flex items-center gap-1.5 shrink-0 disabled:opacity-50"
                      >
                        <Sparkles className="w-3.5 h-3.5" />
                        {isRefining ? "Refining..." : "Refine Spec"}
                      </button>
                    </form>
                  </div>

                  {/* Execution Metrics Bar if available */}
                  {lastExecution && (
                    <div className="glass-card rounded-xl p-4 border border-indigo-500/20 bg-indigo-950/20 flex items-center justify-between">
                      <div className="flex items-center gap-6 text-xs">
                        <div>
                          <span className="text-gray-400">Status:</span>
                          <span className="ml-2 font-semibold text-emerald-400 uppercase">{lastExecution.status}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Rows Written:</span>
                          <span className="ml-2 font-semibold text-white">{lastExecution.metrics?.rows_written || 0}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Duration:</span>
                          <span className="ml-2 font-semibold text-white">{lastExecution.metrics?.duration_seconds || 0}s</span>
                        </div>
                      </div>

                      <button
                        onClick={() => setActiveTab("logs")}
                        className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
                      >
                        <Terminal className="w-3.5 h-3.5" />
                        View Step Logs →
                      </button>
                    </div>
                  )}

                  {/* Tabs Navigation */}
                  <div className="flex items-center gap-2 border-b border-white/10 pb-2">
                    <button
                      onClick={() => setActiveTab("dag")}
                      className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all ${
                        activeTab === "dag" ? "bg-indigo-600/30 text-indigo-300 border border-indigo-500/40" : "text-gray-400 hover:text-white"
                      }`}
                    >
                      <Activity className="w-4 h-4" />
                      DAG Topology
                    </button>

                    <button
                      onClick={() => setActiveTab("code")}
                      className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all ${
                        activeTab === "code" ? "bg-indigo-600/30 text-indigo-300 border border-indigo-500/40" : "text-gray-400 hover:text-white"
                      }`}
                    >
                      <FileCode className="w-4 h-4" />
                      Generated Code
                    </button>

                    <button
                      onClick={() => setActiveTab("airflow")}
                      className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all ${
                        activeTab === "airflow" ? "bg-indigo-600/30 text-cyan-300 border border-cyan-500/40" : "text-gray-400 hover:text-white"
                      }`}
                    >
                      <Wind className="w-4 h-4 text-cyan-400" />
                      Airflow DAG (.py)
                    </button>

                    <button
                      onClick={() => setActiveTab("quality")}
                      className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all ${
                        activeTab === "quality" ? "bg-indigo-600/30 text-emerald-300 border border-emerald-500/40" : "text-gray-400 hover:text-white"
                      }`}
                    >
                      <ShieldCheck className="w-4 h-4 text-emerald-400" />
                      Data Quality Guardrails
                    </button>

                    <button
                      onClick={() => setActiveTab("json")}
                      className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all ${
                        activeTab === "json" ? "bg-indigo-600/30 text-indigo-300 border border-indigo-500/40" : "text-gray-400 hover:text-white"
                      }`}
                    >
                      <Code2 className="w-4 h-4" />
                      JSON Spec
                    </button>

                    <button
                      onClick={() => setActiveTab("lineage")}
                      className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all ${
                        activeTab === "lineage" ? "bg-indigo-600/30 text-amber-300 border border-amber-500/40" : "text-gray-400 hover:text-white"
                      }`}
                    >
                      <Layers className="w-4 h-4 text-amber-400" />
                      Column Lineage Graph
                    </button>

                    <button
                      onClick={() => setActiveTab("logs")}
                      className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all ${
                        activeTab === "logs" ? "bg-indigo-600/30 text-indigo-300 border border-indigo-500/40" : "text-gray-400 hover:text-white"
                      }`}
                    >
                      <Terminal className="w-4 h-4" />
                      Runtime Logs
                    </button>
                  </div>

                  {/* TAB 1: DAG TOPOLOGY */}
                  {activeTab === "dag" && (
                    <div className="glass-card rounded-xl p-6 border border-white/10 space-y-6">
                      <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider">Pipeline Node Topology</h3>

                      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        {nodes.length > 0 ? (
                          nodes.map((node: any, idx: number) => (
                            <div
                              key={node.id || idx}
                              className="p-4 rounded-xl bg-slate-950/80 border border-indigo-500/20 relative shadow-md"
                            >
                              <div className="flex items-center justify-between mb-2">
                                <span className="text-[10px] font-semibold text-indigo-400 uppercase tracking-wider">
                                  {node.type}
                                </span>
                                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                              </div>
                              <h4 className="text-xs font-bold text-white mb-1">{node.label}</h4>
                              <p className="text-[11px] text-gray-400">Status: {node.status}</p>
                            </div>
                          ))
                        ) : (
                          <div className="col-span-4 text-center py-8 text-xs text-gray-500">
                            No DAG nodes defined.
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* TAB 2: GENERATED CODE */}
                  {activeTab === "code" && (
                    <div className="glass-card rounded-xl p-6 border border-white/10 space-y-4">
                      <div className="flex items-center justify-between">
                        <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider">Synthesized Transformation Code</h3>
                        <div className="flex items-center bg-slate-950 p-1 rounded-lg border border-white/10">
                          <button
                            onClick={() => setCodeLang("python")}
                            className={`px-3 py-1 text-xs rounded font-medium ${
                              codeLang === "python" ? "bg-indigo-600 text-white" : "text-gray-400 hover:text-white"
                            }`}
                          >
                            Python / Pandas
                          </button>
                          <button
                            onClick={() => setCodeLang("sql")}
                            className={`px-3 py-1 text-xs rounded font-medium ${
                              codeLang === "sql" ? "bg-indigo-600 text-white" : "text-gray-400 hover:text-white"
                            }`}
                          >
                            SQL
                          </button>
                        </div>
                      </div>

                      <div className="rounded-xl bg-slate-950 p-4 font-mono text-xs text-indigo-200 border border-white/10 overflow-x-auto max-h-96">
                        <pre>{codeLang === "python" ? pythonCode : sqlCode}</pre>
                      </div>
                    </div>
                  )}

                  {/* TAB 3: AIRFLOW DAG EXPORTER */}
                  {activeTab === "airflow" && (
                    <div className="glass-card rounded-xl p-6 border border-white/10 space-y-4">
                      <div className="flex items-center justify-between">
                        <h3 className="text-xs font-bold text-cyan-300 uppercase tracking-wider flex items-center gap-2">
                          <Wind className="w-4 h-4 text-cyan-400" />
                          Apache Airflow DAG Python Export
                        </h3>
                        <button
                          onClick={handleDownloadAirflow}
                          className="bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 text-xs font-semibold px-3 py-1.5 rounded-lg border border-cyan-500/40 flex items-center gap-1.5"
                        >
                          <Download className="w-3.5 h-3.5" />
                          Download DAG (.py)
                        </button>
                      </div>

                      {loadingAirflow ? (
                        <div className="py-8 text-center text-xs text-gray-500">Generating Airflow DAG script...</div>
                      ) : (
                        <div className="rounded-xl bg-slate-950 p-4 font-mono text-xs text-cyan-200 border border-cyan-500/20 overflow-x-auto max-h-96">
                          <pre>{airflowCode}</pre>
                        </div>
                      )}
                    </div>
                  )}

                  {/* TAB 4: DATA QUALITY GUARDRAILS */}
                  {activeTab === "quality" && (
                    <div className="glass-card rounded-xl p-6 border border-white/10 space-y-4">
                      <h3 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-2">
                        <ShieldCheck className="w-4 h-4 text-emerald-400" />
                        Data Quality Guardrail Specifications
                      </h3>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="p-4 rounded-xl bg-slate-950/80 border border-emerald-500/20">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-[10px] font-semibold text-emerald-400 uppercase">Null Rate Check</span>
                            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                          </div>
                          <h4 className="text-xs font-bold text-white">Null Ratio Threshold</h4>
                          <p className="text-[11px] text-gray-400 mt-1">Max 5% null values allowed across primary keys.</p>
                        </div>

                        <div className="p-4 rounded-xl bg-slate-950/80 border border-emerald-500/20">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-[10px] font-semibold text-emerald-400 uppercase">Row Assertion</span>
                            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                          </div>
                          <h4 className="text-xs font-bold text-white">Min Output Row Assertion</h4>
                          <p className="text-[11px] text-gray-400 mt-1">Fails pipeline if ingested record count is 0.</p>
                        </div>

                        <div className="p-4 rounded-xl bg-slate-950/80 border border-emerald-500/20">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-[10px] font-semibold text-emerald-400 uppercase">Schema Integrity</span>
                            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                          </div>
                          <h4 className="text-xs font-bold text-white">Schema Drift Guardrail</h4>
                          <p className="text-[11px] text-gray-400 mt-1">Validates incoming column names match DAG spec.</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* TAB 5: JSON SPEC */}
                  {activeTab === "json" && (
                    <div className="glass-card rounded-xl p-6 border border-white/10 space-y-4">
                      <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider">Full Pipeline Architecture Spec</h3>
                      <div className="rounded-xl bg-slate-950 p-4 font-mono text-xs text-indigo-300 border border-white/10 overflow-x-auto max-h-96">
                        <pre>{JSON.stringify(spec, null, 2)}</pre>
                      </div>
                    </div>
                  )}

                  {/* TAB 6: RUNTIME LOGS */}
                  {activeTab === "logs" && (
                    <div className="glass-card rounded-xl p-6 border border-white/10 space-y-4">
                      <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider flex items-center gap-2">
                        <Terminal className="w-4 h-4 text-emerald-400" />
                        Execution Console & Step Stream
                      </h3>

                      {lastExecution && lastExecution.logs?.length > 0 ? (
                        <div className="rounded-xl bg-black/90 p-4 font-mono text-xs text-emerald-400 border border-emerald-500/20 overflow-x-auto space-y-1 max-h-96">
                          {lastExecution.logs.map((log: any, idx: number) => (
                            <div key={idx} className="flex items-start gap-2">
                              <span className="text-gray-500 shrink-0">[{log.timestamp?.split("T")[1]?.slice(0, 8)}]</span>
                              <span className={`shrink-0 font-bold ${log.level === "ERROR" ? "text-red-400" : log.level === "WARN" ? "text-amber-400" : "text-indigo-400"}`}>
                                [{log.level}]
                              </span>
                              <span className="text-gray-200">{log.message}</span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="py-12 text-center text-xs text-gray-500 border border-dashed border-white/10 rounded-xl">
                          No execution logs found for this pipeline yet. Click &quot;Execute Pipeline&quot; to run.
                        </div>
                      )}
                    </div>
                  )}

                  {/* TAB 7: COLUMN LINEAGE GRAPH */}
                  {activeTab === "lineage" && (
                      <div className="glass-card rounded-xl p-6 border border-white/10 space-y-6">
                        <div className="flex items-center justify-between">
                          <h3 className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-2">
                            <Layers className="w-4 h-4" />
                            Column-Level Data Lineage & Impact Analysis
                          </h3>
                          <span className="text-[10px] px-2.5 py-1 rounded bg-amber-500/10 text-amber-300 font-semibold border border-amber-500/20">
                            Auto-Extracted Graph
                          </span>
                        </div>

                        <div className="space-y-4">
                          {[
                            { col: "user_id", path: ["Ingest (CSV)", "Data Cleaning & Null Handling", "Group By User ID", "SNOWFLAKE Target"] },
                            { col: "email", path: ["Ingest (CSV)", "Clean Missing Email Fields", "Dropped (Nulls Filtered)", "N/A"] },
                            { col: "amount", path: ["Ingest (CSV)", "Cast Float Data Type", "SUM (Daily User Spend)", "SNOWFLAKE Target (total_spend)"] },
                            { col: "transaction_date", path: ["Ingest (CSV)", "Validate ISO Timestamp", "Group By Date", "SNOWFLAKE Target (txn_date)"] },
                          ].map((item, i) => (
                            <div key={i} className="p-4 rounded-xl bg-slate-950/80 border border-amber-500/20 space-y-2">
                              <div className="flex items-center justify-between">
                                <span className="text-xs font-bold text-white font-mono">Field: {item.col}</span>
                                <span className="text-[10px] text-gray-400">Trace Depth: {item.path.length} steps</span>
                              </div>

                              <div className="flex items-center gap-2 overflow-x-auto py-1">
                                {item.path.map((step, idx) => (
                                  <div key={idx} className="flex items-center gap-2 shrink-0">
                                    <span className="text-[11px] px-3 py-1.5 rounded-lg bg-slate-900 text-amber-200 border border-amber-500/30 font-medium">
                                      {step}
                                    </span>
                                    {idx < item.path.length - 1 && (
                                      <span className="text-gray-500 font-bold text-xs">→</span>
                                    )}
                                  </div>
                                ))}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
              </>
              ) : (
                <div className="glass-card rounded-xl p-16 text-center text-gray-500 border border-white/10">
                  Select a pipeline to view details and execute.
                </div>
              )}
            </div>
          </div>
        </main>
      </div>

      {/* AI Prompt Modal */}
      {isAiModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="glass-card rounded-2xl p-6 border border-indigo-500/30 w-full max-w-xl bg-[#0B0F19] shadow-2xl relative">
            <button
              onClick={() => setIsAiModalOpen(false)}
              className="absolute right-4 top-4 text-gray-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-2 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-2">
              <Sparkles className="w-4 h-4" />
              AI Agent Pipeline Synthesizer
            </div>
            <h3 className="text-lg font-bold text-white mb-4">Generate Data Pipeline from Natural Language</h3>

            <form onSubmit={handleGenerateAi} className="space-y-4">
              <textarea
                value={aiPrompt}
                onChange={(e) => setAiPrompt(e.target.value)}
                placeholder="Describe your ETL process in detail. e.g. Extract user transactions CSV from filesystem, clean missing user IDs, aggregate daily spend, and write output to target table."
                rows={4}
                className="w-full bg-slate-950 text-sm text-white placeholder-gray-500 rounded-xl p-4 border border-white/10 focus:outline-none focus:border-indigo-500"
              />

              <div className="flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setIsAiModalOpen(false)}
                  className="px-4 py-2 text-xs font-semibold text-gray-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isGenerating}
                  className="gradient-button text-white text-xs font-semibold px-6 py-2.5 rounded-xl flex items-center gap-2 shadow-lg shadow-indigo-500/20 disabled:opacity-50"
                >
                  {isGenerating ? "Synthesizing Pipeline..." : "Generate Pipeline"}
                  <Sparkles className="w-4 h-4" />
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
