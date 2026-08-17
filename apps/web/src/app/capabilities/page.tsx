"use client";

import Link from "next/link";
import React, { useEffect, useState } from "react";
import {
  type Capability,
  type UserCapability,
  fetchCapabilities,
  fetchUserCapabilities,
} from "../../lib/api";
import { useAuth } from "../../lib/auth-context";

export default function CapabilitiesPage() {
  const { user, isLoading } = useAuth();
  const [capabilities, setCapabilities] = useState<Capability[]>([]);
  const [userCapabilities, setUserCapabilities] = useState<UserCapability[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) return;

    async function load() {
      if (!user) return;
      try {
        const [caps, userCaps] = await Promise.all([
          fetchCapabilities(),
          fetchUserCapabilities(user.id),
        ]);
        setCapabilities(caps);
        setUserCapabilities(userCaps);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load capabilities.");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [user]);

  if (isLoading || loading) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-300">
        <div className="flex items-center space-x-3">
          <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          <span>Loading capabilities...</span>
        </div>
      </main>
    );
  }

  if (!user) {
    return null;
  }

  const userCapMap = new Map(userCapabilities.map((uc) => [uc.capability_id, uc]));

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Link
            href="/dashboard"
            className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-300 bg-clip-text text-transparent"
          >
            CapabilityOS
          </Link>
          <span className="text-xs px-2.5 py-1 bg-indigo-950 border border-indigo-800 text-indigo-300 rounded-full font-medium">
            Capabilities
          </span>
        </div>
      </header>

      <div className="flex-1 max-w-5xl w-full mx-auto p-6 md:p-10">
        <h1 className="text-3xl font-extrabold text-white mb-2">Your Capabilities</h1>
        <p className="text-slate-400 mb-8">
          Track your industry capabilities, proficiency levels, and evidence.
        </p>

        {error && (
          <div className="mb-6 p-4 bg-red-950/60 border border-red-800 rounded-xl text-red-300 text-sm">
            {error}
          </div>
        )}

        {capabilities.length === 0 ? (
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-12 text-center">
            <p className="text-slate-400 text-lg">No capabilities available yet.</p>
            <p className="text-slate-500 text-sm mt-2">
              Complete assessments to build your capability profile.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {capabilities.map((cap) => {
              const userCap = userCapMap.get(cap.id);
              return (
                <div
                  key={cap.id}
                  className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4"
                >
                  <div>
                    <h3 className="text-lg font-semibold text-white">{cap.name}</h3>
                    <p className="text-slate-400 text-sm mt-1">{cap.description}</p>
                    <span className="inline-block mt-2 text-xs px-2 py-1 bg-slate-800 border border-slate-700 text-slate-300 rounded-full">
                      {cap.category}
                    </span>
                  </div>

                  {userCap ? (
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                          Proficiency
                        </span>
                        <span className="text-sm font-medium text-indigo-300">
                          {userCap.proficiency_level}/5
                        </span>
                      </div>
                      <div className="w-full bg-slate-800 rounded-full h-2">
                        <div
                          className="bg-indigo-500 h-2 rounded-full transition-all"
                          style={{ width: `${(userCap.proficiency_level / 5) * 100}%` }}
                        />
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-slate-400">Score</span>
                        <span className="text-slate-200 font-medium">
                          {userCap.score.toFixed(1)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-slate-400">Confidence</span>
                        <span className="text-slate-200 font-medium">
                          {(userCap.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                      {userCap.verified && (
                        <span className="inline-flex items-center px-2 py-1 bg-emerald-950 border border-emerald-800 text-emerald-300 text-xs font-semibold rounded-full">
                          Verified
                        </span>
                      )}
                    </div>
                  ) : (
                    <div className="text-sm text-slate-500">Not yet assessed</div>
                  )}

                  <Link
                    href={`/capabilities/${cap.id}`}
                    className="block w-full text-center py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl transition-all"
                  >
                    View Details
                  </Link>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </main>
  );
}
