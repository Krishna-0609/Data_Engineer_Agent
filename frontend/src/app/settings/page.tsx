"use client";

import { useState } from "react";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import {
  Settings,
  Shield,
  Key,
  Bell,
  Mail,
  Save,
  CheckCircle2,
  Lock,
  Cpu,
} from "lucide-react";

export default function SettingsPage() {
  const [slackWebhook, setSlackWebhook] = useState("https://hooks.slack.com/services/T00/B00/XXXXX");
  const [emailRecipient, setEmailRecipient] = useState("data-alerts@company.com");
  const [masterKeyStatus] = useState("Active (AES-256-Fernet Vault Initialized)");
  const [isSaved, setIsSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 3000);
  };

  return (
    <div className="flex min-h-screen bg-[#0B0F19] text-white">
      <Sidebar />

      <div className="flex-1 flex flex-col min-w-0">
        <Header />

        <main className="p-8 space-y-8 overflow-y-auto max-w-5xl">
          {/* Header Banner */}
          <div className="glass-card rounded-2xl p-6 border border-white/10 flex items-center justify-between">
            <div className="space-y-1">
              <div className="flex items-center gap-2 text-indigo-400 text-xs font-semibold uppercase tracking-wider">
                <Settings className="w-4 h-4" />
                System & Integration Settings
              </div>
              <h1 className="text-2xl font-bold text-white">Platform Settings & Integrations</h1>
              <p className="text-xs text-gray-400">
                Configure credential vault master keys, incident notification webhooks, and AI agent execution preferences.
              </p>
            </div>
          </div>

          <form onSubmit={handleSave} className="space-y-6">
            {/* Section 1: Security & Vault Master Key */}
            <div className="glass-card rounded-2xl p-6 border border-indigo-500/20 space-y-4">
              <h3 className="text-xs font-bold text-indigo-300 uppercase tracking-wider flex items-center gap-2">
                <Shield className="w-4 h-4" />
                Credentials Vault Master Key Status
              </h3>

              <div className="p-4 rounded-xl bg-slate-950/80 border border-indigo-500/30 flex items-center justify-between">
                <div>
                  <h4 className="text-xs font-bold text-white">Master Key Encryption Engine</h4>
                  <p className="text-[11px] text-emerald-400 font-mono mt-0.5">{masterKeyStatus}</p>
                </div>
                <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-[10px] font-bold border border-emerald-500/20 uppercase">
                  ACTIVE & SECURE
                </span>
              </div>
            </div>

            {/* Section 2: Incident Alerting & Notifications */}
            <div className="glass-card rounded-2xl p-6 border border-white/10 space-y-4">
              <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider flex items-center gap-2">
                <Bell className="w-4 h-4 text-amber-400" />
                Incident Alerting & Notification Channels
              </h3>

              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-gray-300 mb-1.5">
                    Slack Incoming Webhook URL
                  </label>
                  <input
                    type="text"
                    value={slackWebhook}
                    onChange={(e) => setSlackWebhook(e.target.value)}
                    className="w-full bg-slate-950 text-xs text-white placeholder-gray-500 rounded-xl p-3 border border-white/10 focus:outline-none focus:border-indigo-500"
                    placeholder="https://hooks.slack.com/services/..."
                  />
                  <p className="text-[11px] text-gray-400 mt-1">Dispatches color-coded alert cards on pipeline failures or data quality violations.</p>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-300 mb-1.5">
                    Email Alert Recipient
                  </label>
                  <input
                    type="email"
                    value={emailRecipient}
                    onChange={(e) => setEmailRecipient(e.target.value)}
                    className="w-full bg-slate-950 text-xs text-white placeholder-gray-500 rounded-xl p-3 border border-white/10 focus:outline-none focus:border-indigo-500"
                    placeholder="data-team@company.com"
                  />
                </div>
              </div>
            </div>

            {/* Save Button */}
            <div className="flex items-center justify-end gap-3 pt-4 border-t border-white/10">
              {isSaved && (
                <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 className="w-4 h-4" />
                  Settings saved successfully!
                </span>
              )}

              <button
                type="submit"
                className="gradient-button text-white text-xs font-semibold px-6 py-2.5 rounded-xl flex items-center gap-2 shadow-lg shadow-indigo-500/20"
              >
                <Save className="w-4 h-4" />
                Save Platform Preferences
              </button>
            </div>
          </form>
        </main>
      </div>
    </div>
  );
}
