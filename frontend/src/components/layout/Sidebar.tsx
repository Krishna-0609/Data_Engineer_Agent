"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  FolderGit2,
  GitFork,
  Activity,
  Bot,
  Settings,
  LogOut,
  ShieldCheck,
  Zap,
  Database,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Projects", href: "/projects", icon: FolderGit2 },
  { name: "Pipelines", href: "/pipelines", icon: GitFork },
  { name: "Data Connections", href: "/connections", icon: Database },
  { name: "AI Agent Studio", href: "/studio", icon: Bot },
  { name: "Execution History", href: "/executions", icon: Activity },
  { name: "Audit Logs", href: "/audit", icon: ShieldCheck },
  { name: "Settings", href: "/settings", icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user_info");
      router.push("/login");
    }
  };

  return (
    <aside className="w-64 bg-[#0F172A]/80 backdrop-blur-xl border-r border-white/10 flex flex-col justify-between h-screen sticky top-0 z-30">
      {/* Brand Header */}
      <div>
        <div className="h-16 flex items-center px-6 border-b border-white/10 gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-base tracking-wide text-white flex items-center gap-1.5">
              DATA AGENT <span className="text-[10px] bg-indigo-500/20 text-indigo-400 px-1.5 py-0.5 rounded border border-indigo-500/30">PRO</span>
            </h1>
            <p className="text-[11px] text-gray-400">Enterprise AI Engine</p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="p-4 space-y-1.5">
          {navigation.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all duration-150",
                  isActive
                    ? "bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 shadow-sm"
                    : "text-gray-400 hover:text-gray-200 hover:bg-white/5"
                )}
              >
                <Icon className={cn("w-4 h-4", isActive ? "text-indigo-400" : "text-gray-400")} />
                {item.name}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Footer User & Logout */}
      <div className="p-4 border-t border-white/10">
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium text-gray-400 hover:text-rose-400 hover:bg-rose-500/10 transition-all border border-transparent hover:border-rose-500/20"
        >
          <LogOut className="w-4 h-4" />
          Sign Out
        </button>
      </div>
    </aside>
  );
}
