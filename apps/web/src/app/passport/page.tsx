"use client";

import Link from "next/link";
import React, { useEffect, useState } from "react";
import { type EngineeringPassport, fetchPassport } from "../../lib/api";
import { useAuth } from "../../lib/auth-context";

export default function PassportPage() {
  const { user, isLoading } = useAuth();
  const [passport, setPassport] = useState<EngineeringPassport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) return;

    async function load() {
      try {
        const data = await fetchPassport();
        setPassport(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load passport.");
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
          <span>Loading Engineering Passport...</span>
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
            href="/dashboard"
            className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-300 bg-clip-text text-transparent"
          >
            CapabilityOS
          </Link>
          <span className="text-xs px-2.5 py-1 bg-indigo-950 border border-indigo-800 text-indigo-300 rounded-full font-medium">
            Engineering Passport
          </span>
        </div>
      </header>

      <div className="flex-1 max-w-5xl w-full mx-auto p-6 md:p-10 space-y-8">
        {error && (
          <div className="p-4 bg-red-950/60 border border-red-800 rounded-xl text-red-300 text-sm">
            {error}
          </div>
        )}

        {passport && (
          <>
            <div className="bg-gradient-to-r from-indigo-900/40 via-slate-900 to-slate-900 border border-indigo-900/50 rounded-2xl p-8 shadow-xl">
              <h1 className="text-3xl font-extrabold text-white">Engineering Passport</h1>
              <p className="text-slate-400 mt-2">
                Aggregated capability evidence and assessment history.
              </p>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4">
              <h2 className="text-lg font-semibold text-slate-200">Profile</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <span className="text-xs text-slate-500 uppercase tracking-wider">Name</span>
                  <p className="text-slate-100 font-medium">
                    {passport.profile.first_name} {passport.profile.last_name}
                  </p>
                </div>
                <div>
                  <span className="text-xs text-slate-500 uppercase tracking-wider">Email</span>
                  <p className="text-slate-100 font-medium">{passport.profile.email}</p>
                </div>
                <div>
                  <span className="text-xs text-slate-500 uppercase tracking-wider">Username</span>
                  <p className="text-indigo-300 font-mono">@{passport.profile.username}</p>
                </div>
                <div>
                  <span className="text-xs text-slate-500 uppercase tracking-wider">Verified</span>
                  <p className="text-slate-100 font-medium">
                    {passport.profile.is_verified ? "Yes" : "No"}
                  </p>
                </div>
                {passport.profile.headline && (
                  <div className="md:col-span-2">
                    <span className="text-xs text-slate-500 uppercase tracking-wider">
                      Headline
                    </span>
                    <p className="text-slate-100 font-medium">{passport.profile.headline}</p>
                  </div>
                )}
                {passport.profile.bio && (
                  <div className="md:col-span-2">
                    <span className="text-xs text-slate-500 uppercase tracking-wider">Bio</span>
                    <p className="text-slate-100 font-medium">{passport.profile.bio}</p>
                  </div>
                )}
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4">
              <h2 className="text-lg font-semibold text-slate-200">
                Capabilities ({passport.capabilities.length})
              </h2>
              {passport.capabilities.length === 0 ? (
                <p className="text-slate-400 text-sm">
                  No capabilities yet. Complete assessments to build your passport.
                </p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {passport.capabilities.map((cap) => (
                    <div
                      key={cap.id}
                      className="bg-slate-950/60 border border-slate-800 rounded-xl p-4"
                    >
                      <div className="flex items-center justify-between">
                        <h3 className="text-sm font-semibold text-white">{cap.name}</h3>
                        <span className="text-xs px-2 py-1 bg-indigo-950 border border-indigo-800 text-indigo-300 rounded-full">
                          {cap.category}
                        </span>
                      </div>
                      <div className="mt-3 grid grid-cols-3 gap-3 text-center">
                        <div>
                          <span className="text-xs text-slate-500">Level</span>
                          <p className="text-sm font-semibold text-indigo-300">
                            {cap.proficiency_level}/5
                          </p>
                        </div>
                        <div>
                          <span className="text-xs text-slate-500">Score</span>
                          <p className="text-sm font-semibold text-white">{cap.score.toFixed(1)}</p>
                        </div>
                        <div>
                          <span className="text-xs text-slate-500">Confidence</span>
                          <p className="text-sm font-semibold text-white">
                            {(cap.confidence * 100).toFixed(0)}%
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4">
              <h2 className="text-lg font-semibold text-slate-200">
                Assessment History ({passport.assessment_history.length})
              </h2>
              {passport.assessment_history.length === 0 ? (
                <p className="text-slate-400 text-sm">No assessments yet.</p>
              ) : (
                <div className="space-y-3">
                  {passport.assessment_history.map((item) => (
                    <div
                      key={item.attempt_id}
                      className="flex items-center justify-between py-3 border-b border-slate-800 last:border-0"
                    >
                      <div>
                        <span className="text-sm font-semibold text-slate-200">
                          {item.assessment_title}
                        </span>
                        <span className="ml-2 text-xs px-2 py-0.5 bg-slate-800 border border-slate-700 text-slate-300 rounded-full">
                          {item.status}
                        </span>
                      </div>
                      <div className="text-right">
                        {item.percentage != null && (
                          <span className="text-sm text-slate-300">
                            {item.percentage.toFixed(0)}%
                          </span>
                        )}
                        {item.submitted_at && (
                          <span className="ml-2 text-xs text-slate-500">
                            {new Date(item.submitted_at).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4">
              <h2 className="text-lg font-semibold text-slate-200">
                Capability History ({passport.capability_history.length})
              </h2>
              {passport.capability_history.length === 0 ? (
                <p className="text-slate-400 text-sm">No capability history yet.</p>
              ) : (
                <div className="space-y-3">
                  {passport.capability_history.map((item) => (
                    <div
                      key={item.id}
                      className="flex items-center justify-between py-3 border-b border-slate-800 last:border-0"
                    >
                      <div>
                        <span className="text-sm text-slate-300">
                          Score: {item.score.toFixed(1)}
                        </span>
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
              )}
            </div>

            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4">
              <h2 className="text-lg font-semibold text-slate-200">
                Project Experience ({passport.project_experience.length})
              </h2>
              {passport.project_experience.length === 0 ? (
                <p className="text-slate-400 text-sm">No project experience yet.</p>
              ) : (
                <div className="space-y-3">
                  {passport.project_experience.map((project) => (
                    <div
                      key={project.id}
                      className="flex items-center justify-between py-3 border-b border-slate-800 last:border-0"
                    >
                      <div>
                        <span className="text-sm font-semibold text-slate-200">{project.name}</span>
                        <span className="ml-2 text-xs px-2 py-0.5 bg-slate-800 border border-slate-700 text-slate-300 rounded-full">
                          {project.status}
                        </span>
                      </div>
                      <span className="text-xs text-slate-500">
                        {new Date(project.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </main>
  );
}
