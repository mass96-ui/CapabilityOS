"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import React, { useEffect, useState } from "react";
import {
  type EngineeringPassport,
  type UserCapability,
  fetchPassport,
  fetchUserCapabilities,
} from "../../lib/api";
import { useAuth } from "../../lib/auth-context";

export default function DashboardPage() {
  const router = useRouter();
  const { user, isLoading, logout } = useAuth();
  const [userCapabilities, setUserCapabilities] = useState<UserCapability[]>([]);
  const [passport, setPassport] = useState<EngineeringPassport | null>(null);
  const [loadingData, setLoadingData] = useState(true);

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login");
    }
  }, [isLoading, user, router]);

  useEffect(() => {
    if (!user) return;

    async function load() {
      if (!user) return;
      try {
        const [userCaps, passportData] = await Promise.all([
          fetchUserCapabilities(user.id),
          fetchPassport(),
        ]);
        setUserCapabilities(userCaps);
        setPassport(passportData);
      } catch {
        // Some data may not exist yet
      } finally {
        setLoadingData(false);
      }
    }

    load();
  }, [user]);

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  if (isLoading || loadingData) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-300">
        <div className="flex items-center space-x-3">
          <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          <span>Loading learner workspace...</span>
        </div>
      </main>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Link
            href="/"
            className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-300 bg-clip-text text-transparent"
          >
            CapabilityOS
          </Link>
          <span className="text-xs px-2.5 py-1 bg-indigo-950 border border-indigo-800 text-indigo-300 rounded-full font-medium">
            Learner Workspace
          </span>
        </div>

        <button
          type="button"
          onClick={handleLogout}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 active:bg-slate-900 border border-slate-700 text-slate-200 text-sm font-medium rounded-xl transition-all cursor-pointer"
        >
          Sign Out
        </button>
      </header>

      <div className="flex-1 max-w-5xl w-full mx-auto p-6 md:p-10 space-y-8">
        <div className="bg-gradient-to-r from-indigo-900/40 via-slate-900 to-slate-900 border border-indigo-900/50 rounded-2xl p-8 shadow-xl">
          <h2 className="text-3xl font-extrabold text-white">
            Welcome back, {user.first_name}! 👋
          </h2>
          <p className="text-slate-400 mt-2 max-w-2xl">
            Track your capabilities, take assessments, and build your Engineering Passport.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Link
            href="/capabilities"
            className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 hover:border-indigo-700 transition-all"
          >
            <h3 className="text-lg font-semibold text-white">Capabilities</h3>
            <p className="text-slate-400 text-sm mt-1">
              {userCapabilities.length} capabilities tracked
            </p>
            <span className="text-indigo-400 text-sm font-medium mt-4 block">
              View Capabilities →
            </span>
          </Link>
          <Link
            href="/assessments"
            className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 hover:border-indigo-700 transition-all"
          >
            <h3 className="text-lg font-semibold text-white">Assessments</h3>
            <p className="text-slate-400 text-sm mt-1">Discover and take assessments</p>
            <span className="text-indigo-400 text-sm font-medium mt-4 block">
              Find Assessments →
            </span>
          </Link>
          <Link
            href="/passport"
            className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 hover:border-indigo-700 transition-all"
          >
            <h3 className="text-lg font-semibold text-white">Engineering Passport</h3>
            <p className="text-slate-400 text-sm mt-1">View your verified capability profile</p>
            <span className="text-indigo-400 text-sm font-medium mt-4 block">View Passport →</span>
          </Link>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 md:p-8 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <h3 className="text-lg font-semibold text-slate-200">Authenticated Learner Profile</h3>
            <span className="inline-flex items-center px-3 py-1 bg-emerald-950 border border-emerald-800 text-emerald-300 text-xs font-semibold rounded-full">
              <span className="w-2 h-2 bg-emerald-400 rounded-full mr-2 animate-pulse" />
              Active Account
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
                Full Name
              </span>
              <span className="text-slate-100 font-medium">
                {user.first_name} {user.last_name}
              </span>
            </div>

            <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
                Username
              </span>
              <span className="text-indigo-300 font-mono font-medium">@{user.username}</span>
            </div>

            <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
                Email Address
              </span>
              <span className="text-slate-100 font-medium">{user.email}</span>
            </div>

            <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
                User ID (UUID)
              </span>
              <span className="text-slate-400 font-mono text-xs truncate block">{user.id}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <Link href="/profile" className="text-indigo-400 hover:text-indigo-300 font-medium">
            Update Profile →
          </Link>
          <Link href="/" className="text-indigo-400 hover:text-indigo-300 font-medium">
            ← Back to Home
          </Link>
        </div>
      </div>
    </main>
  );
}
