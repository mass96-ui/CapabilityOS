"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import React, { useEffect, useState } from "react";
import {
  type Capability,
  type CapabilityScoreHistory,
  type UserCapability,
  fetchCapabilityById,
  fetchCapabilityHistory,
  fetchUserCapabilities,
} from "../../../lib/api";
import { useAuth } from "../../../lib/auth-context";

export default function CapabilityDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { user, isLoading } = useAuth();
  const [capability, setCapability] = useState<Capability | null>(null);
  const [userCap, setUserCap] = useState<UserCapability | null>(null);
  const [history, setHistory] = useState<CapabilityScoreHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) return;

    async function load() {
      if (!user) return;
      try {
        const [cap, userCaps, hist] = await Promise.all([
          fetchCapabilityById(id),
          fetchUserCapabilities(user.id),
          fetchCapabilityHistory(user.id, id),
        ]);
        setCapability(cap);
        setUserCap(userCaps.find((uc: UserCapability) => uc.capability_id === id) || null);
        setHistory(hist);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load capability.");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [user, id]);

  if (isLoading || loading) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-300">
        <div className="flex items-center space-x-3">
          <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          <span>Loading capability...</span>
        </div>
      </main>
    );
  }

  if (!user || !capability) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-300">
        <div className="text-center">
          <p className="text-lg">{error || "Capability not found."}</p>
          <Link
            href="/capabilities"
            className="mt-4 inline-block text-indigo-400 hover:text-indigo-300"
          >
            ← Back to Capabilities
          </Link>
        </div>
      </main>
    );
  }

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
            Capability
          </span>
        </div>
      </header>

      <div className="flex-1 max-w-4xl w-full mx-auto p-6 md:p-10 space-y-8">
        <div>
          <Link
            href="/capabilities"
            className="text-indigo-400 hover:text-indigo-300 text-sm font-medium"
          >
            ← Back to Capabilities
          </Link>
          <h1 className="text-3xl font-extrabold text-white mt-2">{capability.name}</h1>
          <p className="text-slate-400 mt-2">{capability.description}</p>
          <span className="inline-block mt-2 text-xs px-2 py-1 bg-slate-800 border border-slate-700 text-slate-300 rounded-full">
            {capability.category}
          </span>
        </div>

        {userCap && (
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h2 className="text-lg font-semibold text-slate-200">Your Proficiency</h2>
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">Level</span>
              <span className="text-2xl font-bold text-indigo-300">
                {userCap.proficiency_level}/5
              </span>
            </div>
            <div className="w-full bg-slate-800 rounded-full h-3">
              <div
                className="bg-indigo-500 h-3 rounded-full transition-all"
                style={{ width: `${(userCap.proficiency_level / 5) * 100}%` }}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-xs text-slate-500 uppercase tracking-wider">Score</span>
                <p className="text-xl font-semibold text-white">{userCap.score.toFixed(1)}</p>
              </div>
              <div>
                <span className="text-xs text-slate-500 uppercase tracking-wider">Confidence</span>
                <p className="text-xl font-semibold text-white">
                  {(userCap.confidence * 100).toFixed(0)}%
                </p>
              </div>
            </div>
            {userCap.verified && (
              <span className="inline-flex items-center px-2 py-1 bg-emerald-950 border border-emerald-800 text-emerald-300 text-xs font-semibold rounded-full">
                Verified
              </span>
            )}
            {userCap.last_assessed_at && (
              <p className="text-xs text-slate-500">
                Last assessed: {new Date(userCap.last_assessed_at).toLocaleDateString()}
              </p>
            )}
          </div>
        )}

        {history.length > 0 && (
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h2 className="text-lg font-semibold text-slate-200">Score History</h2>
            <div className="space-y-3">
              {history.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between py-2 border-b border-slate-800 last:border-0"
                >
                  <div>
                    <span className="text-sm text-slate-300">Score: {item.score.toFixed(1)}</span>
                    {item.proficiency && (
                      <span className="ml-2 text-xs px-2 py-0.5 bg-indigo-950 border border-indigo-800 text-indigo-300 rounded-full">
                        {item.proficiency}
                      </span>
                    )}
                  </div>
                  <div className="text-right">
                    <span className="text-xs text-slate-500">
                      {new Date(item.created_at).toLocaleDateString()}
                    </span>
                    {item.score_delta !== null && (
                      <span
                        className={`ml-2 text-xs ${item.score_delta >= 0 ? "text-emerald-400" : "text-red-400"}`}
                      >
                        {item.score_delta >= 0 ? "+" : ""}
                        {item.score_delta.toFixed(1)}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {!userCap && (
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-12 text-center">
            <p className="text-slate-400 text-lg">You have not yet demonstrated this capability.</p>
            <Link
              href="/assessments"
              className="mt-4 inline-block px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl transition-all"
            >
              Find Assessments
            </Link>
          </div>
        )}
      </div>
    </main>
  );
}
