"use client";

import { useEffect, useState } from "react";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import {
  ShieldCheck,
  Lock,
  FileText,
  Search,
  Download,
  Key,
  UserCheck,
  Activity,
  CheckCircle2,
} from "lucide-react";
import { formatDate } from "@/lib/utils";

export default function AuditLogsPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [filterAction, setFilterAction] = useState("all");

  const auditLogs = [
    {
      id: "aud_90123801",
      action: "CREDENTIAL_VAULT_ENCRYPTED",
      resource: "Connection: Production S3 Bucket",
      user_email: "test@example.com",
      ip_address: "127.0.0.1",
      status: "SUCCESS",
      timestamp: new Date(Date.now() - 1800000).toISOString(),
    },
    {
      id: "aud_90123802",
      action: "PIPELINE_EXECUTED",
      resource: "Pipeline: ETL — Xtract Customer Transaction Files",
      user_email: "test@example.com",
      ip_address: "127.0.0.1",
      status: "SUCCESS",
      timestamp: new Date(Date.now() - 3600000).toISOString(),
    },
    {
      id: "aud_90123803",
      action: "PROJECT_CREATED",
      resource: "Project: Finance & Sales Analytics",
      user_email: "test@example.com",
      ip_address: "127.0.0.1",
      status: "SUCCESS",
      timestamp: new Date(Date.now() - 86400000).toISOString(),
    },
    {
      id: "aud_90123804",
      action: "CONNECTOR_HEALTH_PING",
      resource: "Connection: Snowflake Warehouse Target",
      user_email: "test@example.com",
      ip_address: "127.0.0.1",
      status: "SUCCESS",
      timestamp: new Date(Date.now() - 172800000).toISOString(),
    },
  ];

  const filtered = auditLogs.filter((log) => {
    const matchesSearch =
      log.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.resource.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.user_email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesAction = filterAction === "all" || log.action === filterAction;
    return matchesSearch && matchesAction;
  });

  return (
    <div className="flex min-h-screen bg-[#0B0F19] text-white">
      <Sidebar />

      <div className="flex-1 flex flex-col min-w-0">
        <Header />

        <main className="p-8 space-y-8 overflow-y-auto">
          {/* Header Banner */}
          <div className="glass-card rounded-2xl p-6 border border-emerald-500/30 bg-gradient-to-r from-emerald-950/30 via-slate-950/40 to-slate-950/60 flex items-center justify-between">
            <div className="space-y-1">
              <div className="flex items-center gap-2 text-emerald-400 text-xs font-semibold uppercase tracking-wider">
                <ShieldCheck className="w-4 h-4" />
                Zero-Trust Compliance & Security
              </div>
              <h1 className="text-2xl font-bold text-white">Security & Access Audit Logs</h1>
              <p className="text-xs text-gray-400">
                Immutable security logs tracking user actions, vault credential access, pipeline executions, and API requests for enterprise compliance.
              </p>
            </div>

            <button className="bg-slate-900 hover:bg-slate-800 text-emerald-300 border border-emerald-500/30 text-xs font-semibold px-4 py-2.5 rounded-xl flex items-center gap-2 transition-all shadow-md">
              <Download className="w-4 h-4" />
              Export Audit CSV
            </button>
          </div>

          {/* Search & Filters */}
          <div className="flex items-center justify-between gap-4">
            <div className="relative flex-1 max-w-md">
              <Search className="w-4 h-4 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search action, resource, or user..."
                className="w-full bg-slate-950 text-xs text-white placeholder-gray-500 rounded-xl pl-10 pr-4 py-2.5 border border-white/10 focus:outline-none focus:border-emerald-500"
              />
            </div>

            <select
              value={filterAction}
              onChange={(e) => setFilterAction(e.target.value)}
              className="bg-slate-950 text-xs text-white px-3 py-2.5 rounded-xl border border-white/10 focus:outline-none"
            >
              <option value="all">All Security Actions</option>
              <option value="CREDENTIAL_VAULT_ENCRYPTED">Credential Encryption</option>
              <option value="PIPELINE_EXECUTED">Pipeline Execution</option>
              <option value="PROJECT_CREATED">Project Creation</option>
              <option value="CONNECTOR_HEALTH_PING">Health Ping</option>
            </select>
          </div>

          {/* Audit Logs Table */}
          <div className="glass-card rounded-2xl border border-white/10 overflow-hidden">
            <table className="w-full text-left text-xs text-gray-300">
              <thead className="bg-slate-950/80 text-gray-400 uppercase font-mono text-[10px] tracking-wider border-b border-white/10">
                <tr>
                  <th className="px-6 py-4">Audit ID</th>
                  <th className="px-6 py-4">Action Event</th>
                  <th className="px-6 py-4">Target Resource</th>
                  <th className="px-6 py-4">User</th>
                  <th className="px-6 py-4">IP Address</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4 text-right">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {filtered.map((log) => (
                  <tr key={log.id} className="hover:bg-white/5 transition-all">
                    <td className="px-6 py-4 font-mono text-emerald-400">{log.id}</td>
                    <td className="px-6 py-4">
                      <span className="px-2.5 py-1 rounded bg-slate-900 font-mono text-[11px] font-bold text-white border border-white/10">
                        {log.action}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-medium text-gray-200">{log.resource}</td>
                    <td className="px-6 py-4 text-gray-400">{log.user_email}</td>
                    <td className="px-6 py-4 font-mono text-gray-400">{log.ip_address}</td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        {log.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right text-gray-400">{formatDate(log.timestamp)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </main>
      </div>
    </div>
  );
}
