"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function RootPage() {
  const router = useRouter();

  useEffect(() => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("access_token");
      if (token) {
        router.replace("/dashboard");
      } else {
        router.replace("/login");
      }
    }
  }, [router]);

  return (
    <div className="min-h-screen bg-[#0B0F19] flex items-center justify-center text-xs text-gray-500">
      Loading AI Data Engineer Agent Platform...
    </div>
  );
}
