"use client";

import { useEffect, useState } from "react";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import {
  Database,
  Plus,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Lock,
  X,
  Server,
  Cloud,
  BarChart3,
  Globe,
  Radio,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { formatDate } from "@/lib/utils";

export default function ConnectionsPage() {
  const [projects, setProjects] = useState<any[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [connections, setConnections] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [connType, setConnType] = useState<string>("aws_s3");
  const [connCategory, setConnCategory] = useState<string>("source");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form Fields State for dynamic connector types
  const [s3Bucket, setS3Bucket] = useState("");
  const [s3Region, setS3Region] = useState("us-east-1");
  const [s3AccessKey, setS3AccessKey] = useState("");
  const [s3SecretKey, setS3SecretKey] = useState("");

  const [dbHost, setDbHost] = useState("");
  const [dbPort, setDbPort] = useState(5432);
  const [dbName, setDbName] = useState("");
  const [dbUser, setDbUser] = useState("");
  const [dbPassword, setDbPassword] = useState("");

  const [qsDatasetId, setQsDatasetId] = useState("");
  const [qsRegion, setQsRegion] = useState("us-east-1");
  const [qsRoleArn, setQsRoleArn] = useState("");

  const [pbiWorkspaceId, setPbiWorkspaceId] = useState("");
  const [pbiDatasetId, setPbiDatasetId] = useState("");
  const [pbiTenantId, setPbiTenantId] = useState("");
  const [pbiClientId, setPbiClientId] = useState("");
  const [pbiClientSecret, setPbiClientSecret] = useState("");

  // Testing status map: connectionId -> { testing: bool, result: any }
  const [testResults, setTestResults] = useState<Record<string, any>>({});

  useEffect(() => {
    async function init() {
      try {
        const res = await apiClient.get("/projects/");
        const items = res.data.items || [];
        setProjects(items);

        if (items.length > 0) {
          const pId = items[0].id;
          setSelectedProjectId(pId);
          await loadConnections(pId);
        }
      } catch (err) {
        console.error("Init error:", err);
      }
    }
    init();
  }, []);

  async function loadConnections(projectId: string) {
    setLoading(true);
    try {
      const res = await apiClient.get(`/connections/?project_id=${projectId}`);
      setConnections(res.data.items || []);
    } catch (err) {
      console.error("Load connections error:", err);
    } finally {
      setLoading(false);
    }
  }

  const handleTestConnection = async (connId: string) => {
    setTestResults((prev) => ({ ...prev, [connId]: { testing: true } }));
    try {
      const res = await apiClient.post(`/connections/${connId}/test`);
      setTestResults((prev) => ({
        ...prev,
        [connId]: { testing: false, result: res.data },
      }));
    } catch (err: any) {
      setTestResults((prev) => ({
        ...prev,
        [connId]: {
          testing: false,
          result: { healthy: false, message: err.response?.data?.detail || "Health check failed." },
        },
      }));
    }
  };

  const handleCreateConnection = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !selectedProjectId) return;
    setIsSubmitting(true);

    let config: Record<string, any> = {};

    if (connType === "aws_s3") {
      config = {
        bucket_name: s3Bucket,
        region: s3Region,
        aws_access_key_id: s3AccessKey,
        aws_secret_access_key: s3SecretKey,
      };
    } else if (connType === "aws_rds_postgres" || connType === "aws_rds_mysql") {
      config = {
        host: dbHost,
        port: Number(dbPort),
        database: dbName,
        username: dbUser,
        password: dbPassword,
      };
    } else if (connType === "aws_quicksight") {
      config = {
        dataset_id: qsDatasetId,
        region: qsRegion,
        role_arn: qsRoleArn,
      };
    } else if (connType === "power_bi") {
      config = {
        workspace_id: pbiWorkspaceId,
        dataset_id: pbiDatasetId,
        tenant_id: pbiTenantId,
        client_id: pbiClientId,
        client_secret: pbiClientSecret,
      };
    }

    try {
      await apiClient.post("/connections/", {
        project_id: selectedProjectId,
        name: name.trim(),
        category: connCategory,
        connection_type: connType,
        description: description.trim() || null,
        config,
      });

      setIsModalOpen(false);
      resetForm();
      await loadConnections(selectedProjectId);
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      const errorMsg =
        typeof detail === "string"
          ? detail
          : Array.isArray(detail)
          ? detail.map((d: any) => `${d.loc?.join(".") || "field"}: ${d.msg}`).join("\n")
          : "Failed to create connection.";
      alert(errorMsg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setName("");
    setDescription("");
    setS3Bucket("");
    setS3AccessKey("");
    setS3SecretKey("");
    setDbHost("");
    setDbName("");
    setDbUser("");
    setDbPassword("");
    setQsDatasetId("");
    setQsRoleArn("");
    setPbiWorkspaceId("");
    setPbiDatasetId("");
    setPbiTenantId("");
    setPbiClientId("");
    setPbiClientSecret("");
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
              <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
                <Database className="w-6 h-6 text-indigo-400" />
                Data Connections & Security Vault
              </h1>
              <p className="text-sm text-gray-400 mt-1">
                Configure encrypted connections to AWS S3, RDS, Snowflake, and BI analytics endpoints (QuickSight & Power BI).
              </p>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-gray-400">Project:</span>
                <select
                  value={selectedProjectId}
                  onChange={(e) => {
                    setSelectedProjectId(e.target.value);
                    loadConnections(e.target.value);
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

              <button
                onClick={() => setIsModalOpen(true)}
                className="gradient-button text-white text-xs font-semibold px-4 py-2.5 rounded-xl flex items-center gap-2 shadow-lg shadow-indigo-500/20"
              >
                <Plus className="w-4 h-4" />
                Add New Connector
              </button>
            </div>
          </div>

          {/* Security Banner */}
          <div className="glass-card rounded-xl p-4 border border-indigo-500/20 bg-indigo-950/20 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-indigo-500/20 flex items-center justify-center border border-indigo-500/30">
                <Lock className="w-4 h-4 text-indigo-300" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-white">AES-256 Fernet Encryption Vault Active</h4>
                <p className="text-[11px] text-gray-400">Credentials are encrypted at rest and masked in zero-trust responses.</p>
              </div>
            </div>

            <span className="text-xs px-2.5 py-1 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5" />
              Zero-Trust Compliant
            </span>
          </div>

          {/* Connections Grid */}
          {loading ? (
            <div className="py-16 text-center text-xs text-gray-500">Loading connection registry...</div>
          ) : connections.length === 0 ? (
            <div className="glass-card rounded-2xl p-16 text-center text-gray-500 border border-white/10 space-y-4">
              <Database className="w-10 h-10 text-gray-600 mx-auto" />
              <h3 className="text-sm font-semibold text-white">No Connections Configured</h3>
              <p className="text-xs text-gray-400 max-w-sm mx-auto">
                Add AWS S3 buckets, RDS PostgreSQL databases, or BI analytics endpoints to enable AI pipeline synthesis.
              </p>
              <button
                onClick={() => setIsModalOpen(true)}
                className="gradient-button text-white text-xs font-semibold px-4 py-2 rounded-xl"
              >
                Create Connector
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {connections.map((conn) => {
                const tRes = testResults[conn.id];
                const isTesting = tRes?.testing;
                const health = tRes?.result;

                return (
                  <div key={conn.id} className="glass-card rounded-xl p-5 border border-white/10 space-y-4 relative">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {conn.connection_type.includes("s3") ? (
                          <Cloud className="w-5 h-5 text-sky-400" />
                        ) : conn.connection_type.includes("rds") ? (
                          <Server className="w-5 h-5 text-indigo-400" />
                        ) : (
                          <BarChart3 className="w-5 h-5 text-amber-400" />
                        )}
                        <h3 className="text-sm font-bold text-white">{conn.name}</h3>
                      </div>

                      <span className="text-[10px] px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 font-mono uppercase">
                        {conn.category}
                      </span>
                    </div>

                    <p className="text-xs text-gray-400 line-clamp-2">{conn.description || "Secure data connector."}</p>

                    {/* Masked Config Summary */}
                    <div className="rounded-lg bg-slate-950/80 p-3 space-y-1 text-[11px] font-mono border border-white/5">
                      {Object.entries(conn.config).map(([k, v]) => (
                        <div key={k} className="flex justify-between items-center text-gray-400">
                          <span className="text-gray-500">{k}:</span>
                          <span className="text-gray-200 truncate max-w-[160px]">{String(v)}</span>
                        </div>
                      ))}
                    </div>

                    {/* Health Check Bar */}
                    <div className="pt-2 border-t border-white/5 flex items-center justify-between">
                      <button
                        onClick={() => handleTestConnection(conn.id)}
                        disabled={isTesting}
                        className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1.5 disabled:opacity-50"
                      >
                        <RefreshCw className={`w-3.5 h-3.5 ${isTesting ? "animate-spin" : ""}`} />
                        {isTesting ? "Testing Ping..." : "Test Connection"}
                      </button>

                      {health && (
                        <div className="flex items-center gap-1.5 text-xs">
                          {health.healthy ? (
                            <span className="text-emerald-400 font-semibold flex items-center gap-1">
                              <CheckCircle2 className="w-3.5 h-3.5" />
                              Healthy ({health.latency_ms}ms)
                            </span>
                          ) : (
                            <span className="text-rose-400 font-semibold flex items-center gap-1">
                              <AlertCircle className="w-3.5 h-3.5" />
                              Failed
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </main>
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="glass-card rounded-2xl p-6 border border-indigo-500/30 w-full max-w-xl bg-[#0B0F19] shadow-2xl relative max-h-[90vh] overflow-y-auto">
            <button onClick={() => setIsModalOpen(false)} className="absolute right-4 top-4 text-gray-400 hover:text-white">
              <X className="w-5 h-5" />
            </button>

            <h3 className="text-lg font-bold text-white mb-4">Configure New Secure Data Connector</h3>

            <form onSubmit={handleCreateConnection} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-gray-400 block mb-1">Connector Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Production AWS S3 Transactions"
                  className="w-full bg-slate-950 text-sm text-white rounded-lg p-2.5 border border-white/10 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-semibold text-gray-400 block mb-1">Connector Type</label>
                  <select
                    value={connType}
                    onChange={(e) => setConnType(e.target.value)}
                    className="w-full bg-slate-950 text-sm text-white rounded-lg p-2.5 border border-white/10 focus:outline-none focus:border-indigo-500"
                  >
                    <option value="aws_s3">AWS S3 Bucket</option>
                    <option value="aws_rds_postgres">AWS RDS PostgreSQL</option>
                    <option value="aws_rds_mysql">AWS RDS MySQL</option>
                    <option value="aws_quicksight">AWS QuickSight BI Endpoint</option>
                    <option value="power_bi">Power BI Analytics Endpoint</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs font-semibold text-gray-400 block mb-1">Category</label>
                  <select
                    value={connCategory}
                    onChange={(e) => setConnCategory(e.target.value)}
                    className="w-full bg-slate-950 text-sm text-white rounded-lg p-2.5 border border-white/10 focus:outline-none focus:border-indigo-500"
                  >
                    <option value="source">Source</option>
                    <option value="destination">Destination</option>
                    <option value="bi_analytics">BI Analytics</option>
                  </select>
                </div>
              </div>

              {/* Dynamic Credential Fields */}
              {connType === "aws_s3" && (
                <div className="space-y-3 p-4 rounded-xl bg-slate-950/80 border border-white/5">
                  <h4 className="text-xs font-bold text-sky-400">AWS S3 Configuration</h4>
                  <input
                    type="text"
                    placeholder="S3 Bucket Name (e.g. prod-customer-data)"
                    value={s3Bucket}
                    onChange={(e) => setS3Bucket(e.target.value)}
                    className="w-full bg-slate-900 text-xs text-white p-2 rounded border border-white/10"
                  />
                  <input
                    type="text"
                    placeholder="AWS Region (e.g. us-east-1)"
                    value={s3Region}
                    onChange={(e) => setS3Region(e.target.value)}
                    className="w-full bg-slate-900 text-xs text-white p-2 rounded border border-white/10"
                  />
                  <input
                    type="text"
                    placeholder="AWS Access Key ID (AKIA...)"
                    value={s3AccessKey}
                    onChange={(e) => setS3AccessKey(e.target.value)}
                    className="w-full bg-slate-900 text-xs text-white p-2 rounded border border-white/10"
                  />
                  <input
                    type="password"
                    placeholder="AWS Secret Access Key"
                    value={s3SecretKey}
                    onChange={(e) => setS3SecretKey(e.target.value)}
                    className="w-full bg-slate-900 text-xs text-white p-2 rounded border border-white/10"
                  />
                </div>
              )}

              {(connType === "aws_rds_postgres" || connType === "aws_rds_mysql") && (
                <div className="space-y-3 p-4 rounded-xl bg-slate-950/80 border border-white/5">
                  <h4 className="text-xs font-bold text-indigo-400">Database Credentials</h4>
                  <div className="grid grid-cols-3 gap-2">
                    <input
                      type="text"
                      placeholder="Host (db.rds.amazonaws.com)"
                      value={dbHost}
                      onChange={(e) => setDbHost(e.target.value)}
                      className="col-span-2 bg-slate-900 text-xs text-white p-2 rounded border border-white/10"
                    />
                    <input
                      type="number"
                      placeholder="Port"
                      value={dbPort}
                      onChange={(e) => setDbPort(Number(e.target.value))}
                      className="bg-slate-900 text-xs text-white p-2 rounded border border-white/10"
                    />
                  </div>
                  <input
                    type="text"
                    placeholder="Database Name"
                    value={dbName}
                    onChange={(e) => setDbName(e.target.value)}
                    className="w-full bg-slate-900 text-xs text-white p-2 rounded border border-white/10"
                  />
                  <div className="grid grid-cols-2 gap-2">
                    <input
                      type="text"
                      placeholder="Username"
                      value={dbUser}
                      onChange={(e) => setDbUser(e.target.value)}
                      className="bg-slate-900 text-xs text-white p-2 rounded border border-white/10"
                    />
                    <input
                      type="password"
                      placeholder="Password"
                      value={dbPassword}
                      onChange={(e) => setDbPassword(e.target.value)}
                      className="bg-slate-900 text-xs text-white p-2 rounded border border-white/10"
                    />
                  </div>
                </div>
              )}

              {connType === "aws_quicksight" && (
                <div className="space-y-3 p-4 rounded-xl bg-slate-950/80 border border-white/5">
                  <h4 className="text-xs font-bold text-amber-400">AWS QuickSight Configuration</h4>
                  <input
                    type="text"
                    placeholder="QuickSight DataSet ID"
                    value={qsDatasetId}
                    onChange={(e) => setQsDatasetId(e.target.value)}
                    className="w-full bg-slate-900 text-xs text-white p-2 rounded border border-white/10"
                  />
                  <input
                    type="text"
                    placeholder="AWS Service Role ARN (arn:aws:iam::...)"
                    value={qsRoleArn}
                    onChange={(e) => setQsRoleArn(e.target.value)}
                    className="w-full bg-slate-900 text-xs text-white p-2 rounded border border-white/10"
                  />
                </div>
              )}

              {connType === "power_bi" && (
                <div className="space-y-3 p-4 rounded-xl bg-slate-950/80 border border-white/5">
                  <h4 className="text-xs font-bold text-amber-400">Power BI Service Principal Config</h4>
                  <input
                    type="text"
                    placeholder="Power BI Workspace ID"
                    value={pbiWorkspaceId}
                    onChange={(e) => setPbiWorkspaceId(e.target.value)}
                    className="w-full bg-slate-900 text-xs text-white p-2 rounded border border-white/10"
                  />
                  <input
                    type="text"
                    placeholder="Dataset ID"
                    value={pbiDatasetId}
                    onChange={(e) => setPbiDatasetId(e.target.value)}
                    className="w-full bg-slate-900 text-xs text-white p-2 rounded border border-white/10"
                  />
                  <input
                    type="password"
                    placeholder="Service Principal Client Secret"
                    value={pbiClientSecret}
                    onChange={(e) => setPbiClientSecret(e.target.value)}
                    className="w-full bg-slate-900 text-xs text-white p-2 rounded border border-white/10"
                  />
                </div>
              )}

              <div className="flex items-center justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-xs font-semibold text-gray-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="gradient-button text-white text-xs font-semibold px-6 py-2.5 rounded-xl disabled:opacity-50"
                >
                  {isSubmitting ? "Encrypting & Saving..." : "Save Connection"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
