"use client";

import Link from "next/link";
import React, { useEffect, useState } from "react";
import { fetchHealth } from "../lib/api";
import { useAuth } from "../lib/auth-context";

export default function HomePage() {
  const { user, isAuthenticated } = useAuth();
  const [healthStatus, setHealthStatus] = useState<string>("Checking...");
  const [isApiOnline, setIsApiOnline] = useState<boolean>(false);

  useEffect(() => {
    fetchHealth()
      .then((res) => {
        if (res.status === "healthy") {
          setHealthStatus("FastAPI Backend Online");
          setIsApiOnline(true);
        } else {
          setHealthStatus(`Backend response: ${res.status}`);
        }
      })
      .catch(() => {
        setHealthStatus("Backend Offline (Start Uvicorn on :8000)");
        setIsApiOnline(false);
      });
  }, []);

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between p-6 md:p-12">
      {/* Header */}
      <header className="max-w-6xl w-full mx-auto flex items-center justify-between py-4">
        <div className="flex items-center space-x-3">
          <span className="text-2xl font-black bg-gradient-to-r from-blue-400 via-indigo-300 to-purple-400 bg-clip-text text-transparent">
            CapabilityOS
          </span>
          <span className="text-xs px-2.5 py-0.5 bg-slate-800 border border-slate-700 text-slate-300 rounded-full font-medium">
            v1.0.0
          </span>
        </div>

        <div className="flex items-center space-x-4">
          {isAuthenticated ? (
            <Link
              href="/dashboard"
              className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm rounded-xl shadow-lg shadow-indigo-600/20 transition-all"
            >
              Go to Dashboard ({user?.first_name})
            </Link>
          ) : (
            <>
              <Link
                href="/login"
                className="px-4 py-2 text-slate-300 hover:text-white text-sm font-semibold transition-all"
              >
                Sign In
              </Link>
              <Link
                href="/register"
                className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm rounded-xl shadow-lg shadow-indigo-600/20 transition-all"
              >
                Get Started
              </Link>
            </>
          )}
        </div>
      </header>

      {/* Hero Section */}
      <div className="max-w-4xl w-full mx-auto my-auto text-center py-16 space-y-8">
        <div className="inline-flex items-center space-x-2 px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-full text-xs text-slate-300">
          <span
            className={`w-2 h-2 rounded-full ${
              isApiOnline ? "bg-emerald-400 animate-pulse" : "bg-amber-500"
            }`}
          />
          <span>{healthStatus}</span>
        </div>

        <h1 className="text-4xl md:text-6xl font-black tracking-tight leading-tight">
          Practical Industry Experience <br />
          <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-purple-400 bg-clip-text text-transparent">
            Powered by CapabilityOS
          </span>
        </h1>

        <p className="text-slate-400 text-lg max-w-2xl mx-auto leading-relaxed">
          Build real capability through hands-on work, assessments, and manager-guided project
          execution.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
          <Link
            href="/register"
            className="w-full sm:w-auto px-8 py-4 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-base rounded-2xl shadow-xl shadow-indigo-600/25 transition-all"
          >
            Register as Learner
          </Link>
          <Link
            href="/login"
            className="w-full sm:w-auto px-8 py-4 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-200 font-semibold text-base rounded-2xl transition-all"
          >
            Learner Login
          </Link>
        </div>
      </div>

      {/* Footer Info */}
      <footer className="max-w-6xl w-full mx-auto pt-8 border-t border-slate-900 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 space-y-2 sm:space-y-0">
        <div>CapabilityOS Learner App (`apps/web`)</div>
        <div>FastAPI Backend (`http://localhost:8000/api/v1`)</div>
      </footer>
    </main>
  );
}
