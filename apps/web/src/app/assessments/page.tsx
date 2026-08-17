"use client";

import Link from "next/link";
import React, { useEffect, useState } from "react";
import {
  type Assessment,
  type UserCapability,
  fetchAssessments,
  fetchUserCapabilities,
} from "../../lib/api";
import { useAuth } from "../../lib/auth-context";

export default function AssessmentsPage() {
  const { user, isLoading } = useAuth();
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [userCapabilities, setUserCapabilities] = useState<UserCapability[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) return;

    async function load() {
      if (!user) return;
      try {
        const [assessmentsData, userCaps] = await Promise.all([
          fetchAssessments(),
          fetchUserCapabilities(user.id),
        ]);
        setAssessments(assessmentsData);
        setUserCapabilities(userCaps);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load assessments.");
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
          <span>Loading assessments...</span>
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
            Assessments
          </span>
        </div>
      </header>

      <div className="flex-1 max-w-5xl w-full mx-auto p-6 md:p-10">
        <h1 className="text-3xl font-extrabold text-white mb-2">Assessments</h1>
        <p className="text-slate-400 mb-8">
          Discover assessments to validate and improve your capabilities.
        </p>

        {error && (
          <div className="mb-6 p-4 bg-red-950/60 border border-red-800 rounded-xl text-red-300 text-sm">
            {error}
          </div>
        )}

        {assessments.length === 0 ? (
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-12 text-center">
            <p className="text-slate-400 text-lg">No assessments available yet.</p>
            <p className="text-slate-500 text-sm mt-2">Check back later for new assessments.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {assessments.map((assessment) => (
              <div
                key={assessment.id}
                className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4"
              >
                <div>
                  <h3 className="text-lg font-semibold text-white">{assessment.title}</h3>
                  <p className="text-slate-400 text-sm mt-1">{assessment.description}</p>
                  <div className="flex items-center space-x-2 mt-3">
                    <span className="text-xs px-2 py-1 bg-slate-800 border border-slate-700 text-slate-300 rounded-full">
                      {assessment.difficulty}
                    </span>
                    {assessment.time_limit_minutes && (
                      <span className="text-xs px-2 py-1 bg-slate-800 border border-slate-700 text-slate-300 rounded-full">
                        {assessment.time_limit_minutes} min
                      </span>
                    )}
                  </div>
                </div>

                <Link
                  href={`/assessments/${assessment.id}/attempt`}
                  className="block w-full text-center py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl transition-all"
                >
                  Start Assessment
                </Link>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
