"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import React, { useEffect, useState } from "react";
import {
  type Project,
  type ProjectMatchResult,
  type ProjectRequirement,
  fetchProjectById,
  fetchProjectMatch,
  fetchProjectRequirements,
} from "../../../lib/api";
import { useAuth } from "../../../lib/auth-context";

export default function ProjectDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuth();
  const [project, setProject] = useState<Project | null>(null);
  const [requirements, setRequirements] = useState<ProjectRequirement[]>([]);
  const [match, setMatch] = useState<ProjectMatchResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    }
  }, [authLoading, user, router]);

  useEffect(() => {
    if (!user) return;
    loadData();
  }, [user]);

  async function loadData() {
    setLoading(true);
    setError(null);
    try {
      const [projectData, reqData] = await Promise.all([
        fetchProjectById(params.id),
        fetchProjectRequirements(params.id),
      ]);
      setProject(projectData);
      setRequirements(reqData);
      try {
        const matchData = await fetchProjectMatch(params.id);
        setMatch(matchData);
      } catch {
        // No match data available
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load project");
    } finally {
      setLoading(false);
    }
  }

  if (authLoading || loading) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-white text-slate-600">
        <div className="flex items-center space-x-3">
          <div className="w-5 h-5 border-2 border-slate-900 border-t-transparent rounded-full animate-spin" />
          <span className="text-sm font-medium">Loading project...</span>
        </div>
      </main>
    );
  }

  if (!project) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-white text-slate-600">
        <p>Project not found.</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-white text-slate-900 flex flex-col">
      <header className="border-b border-slate-200 bg-white px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Link href="/" className="text-lg font-semibold text-slate-900">
            CapabilityOS
          </Link>
          <span className="text-xs px-2.5 py-1 bg-slate-100 border border-slate-200 text-slate-600 rounded-full font-medium">
            Projects
          </span>
        </div>
        <Link href="/projects" className="text-slate-500 hover:text-slate-700 font-medium text-sm">
          Back to Projects
        </Link>
      </header>

      <div className="flex-1 max-w-5xl w-full mx-auto p-6 md:p-10 space-y-8">
        <div className="border border-slate-200 rounded-xl p-6 md:p-8">
          <div className="flex items-center gap-3 mb-4">
            <h1 className="text-2xl font-semibold text-slate-900">{project.name}</h1>
            <span
              className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                project.status === "open"
                  ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                  : project.status === "draft"
                    ? "bg-slate-100 text-slate-600 border border-slate-200"
                    : "bg-amber-50 text-amber-700 border border-amber-200"
              }`}
            >
              {project.status}
            </span>
            <span className="inline-flex items-center px-2 py-0.5 bg-slate-100 border border-slate-200 text-slate-600 rounded text-xs font-medium">
              {project.project_type}
            </span>
          </div>
          <p className="text-slate-600 text-sm max-w-2xl">
            {project.description || "No description provided."}
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 text-sm">
            {error}
          </div>
        )}

        {match && (
          <div className="border border-slate-200 rounded-xl p-6 md:p-8 space-y-6">
            <div className="flex items-center justify-between border-b border-slate-200 pb-4">
              <h2 className="text-lg font-semibold text-slate-900">Your Match</h2>
              <div className="flex items-center gap-3">
                <span
                  className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                    match.eligible
                      ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                      : "bg-red-50 text-red-700 border border-red-200"
                  }`}
                >
                  {match.eligible ? "Eligible" : "Not Eligible"}
                </span>
                <span className="text-xl font-semibold text-slate-900">{match.match_score}%</span>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 text-center">
                <p className="text-slate-500 text-xs font-medium">Matched</p>
                <p className="text-xl font-semibold text-emerald-600 mt-1">
                  {match.matched.length}
                </p>
              </div>
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 text-center">
                <p className="text-slate-500 text-xs font-medium">Gaps</p>
                <p className="text-xl font-semibold text-amber-600 mt-1">{match.gaps.length}</p>
              </div>
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 text-center">
                <p className="text-slate-500 text-xs font-medium">Missing</p>
                <p className="text-xl font-semibold text-red-600 mt-1">{match.missing.length}</p>
              </div>
            </div>

            {match.matched.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wider mb-3">
                  Matched Capabilities
                </h3>
                <div className="space-y-2">
                  {match.matched.map((m) => (
                    <div
                      key={m.requirement_id}
                      className="bg-slate-50 border border-emerald-200 rounded-lg p-3 flex items-center justify-between"
                    >
                      <span className="text-slate-900 text-sm">
                        {m.capability_name || m.capability_id}
                      </span>
                      <span className="text-xs text-emerald-700 font-medium">
                        Level {m.required_level}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {match.gaps.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wider mb-3">
                  Capability Gaps
                </h3>
                <div className="space-y-2">
                  {match.gaps.map((g) => (
                    <div
                      key={g.requirement_id}
                      className="bg-slate-50 border border-amber-200 rounded-lg p-3 flex items-center justify-between"
                    >
                      <span className="text-slate-900 text-sm">
                        {g.capability_name || g.capability_id}
                      </span>
                      <span className="text-xs text-amber-700 font-medium">
                        Gap: {g.gap} levels
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {match.missing.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wider mb-3">
                  Missing Capabilities
                </h3>
                <div className="space-y-2">
                  {match.missing.map((m) => (
                    <div
                      key={m.requirement_id}
                      className="bg-slate-50 border border-red-200 rounded-lg p-3 flex items-center justify-between"
                    >
                      <span className="text-slate-900 text-sm">
                        {m.capability_name || m.capability_id}
                      </span>
                      <span className="text-xs text-red-700 font-medium">
                        Required: Level {m.required_level}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        <div className="border border-slate-200 rounded-xl p-6 md:p-8 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-200 pb-4">
            <h2 className="text-lg font-semibold text-slate-900">Required Capabilities</h2>
            <span className="text-slate-500 text-sm">{requirements.length} requirements</span>
          </div>

          {requirements.length === 0 ? (
            <p className="text-slate-500 text-center py-4 text-sm">
              No requirements defined for this project yet.
            </p>
          ) : (
            <div className="space-y-3">
              {requirements.map((req) => (
                <div
                  key={req.id}
                  className="bg-slate-50 border border-slate-200 rounded-lg p-4 flex items-center justify-between"
                >
                  <div>
                    <p className="text-slate-900 font-medium text-sm">
                      {req.capability_name || req.capability_id}
                    </p>
                    <p className="text-slate-500 text-xs mt-1">
                      Min proficiency: {req.minimum_proficiency_level} | Importance:{" "}
                      {req.importance}
                    </p>
                    {req.description && (
                      <p className="text-slate-400 text-xs mt-1">{req.description}</p>
                    )}
                  </div>
                  <span
                    className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                      req.required ? "bg-slate-900 text-white" : "bg-slate-200 text-slate-700"
                    }`}
                  >
                    {req.required ? "Required" : "Optional"}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
