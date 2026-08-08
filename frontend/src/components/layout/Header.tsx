"use client";

import { useEffect, useState } from "react";
import { Search, Bell, CheckCircle2, User } from "lucide-react";

export default function Header() {
  const [userEmail, setUserEmail] = useState<string>("Data Engineer");

  useEffect(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("user_info");
      if (stored) {
        try {
          const parsed = JSON.parse(stored);
          setUserEmail(parsed.email || parsed.full_name || "Data Engineer");
        } catch {
          // default
        }
      }
    }
  }, []);

  return (
    <header className="h-16 border-b border-white/10 bg-[#0F172A]/50 backdrop-blur-md px-8 flex items-center justify-between sticky top-0 z-20">
      {/* Global Search Bar */}
      <div className="relative w-96">
        <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          placeholder="Search pipelines, projects, executions..."
          className="w-full bg-slate-900/80 text-sm text-gray-200 placeholder-gray-500 rounded-lg pl-9 pr-4 py-2 border border-white/10 focus:outline-none focus:border-indigo-500/60 transition-all"
        />
      </div>

      {/* System Status & User Profile */}
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          Backend API Live
        </div>

        <button className="relative p-2 rounded-lg text-gray-400 hover:text-gray-200 hover:bg-white/5 transition-all">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-indigo-500 rounded-full" />
        </button>

        <div className="h-6 w-px bg-white/10" />

        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold border border-white/20">
            <User className="w-4 h-4" />
          </div>
          <div className="text-left">
            <p className="text-xs font-medium text-gray-200">{userEmail}</p>
            <p className="text-[10px] text-gray-400">Enterprise Admin</p>
          </div>
        </div>
      </div>
    </header>
  );
}
