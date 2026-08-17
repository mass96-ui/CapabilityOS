"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import React, { useEffect, useState } from "react";
import {
  type Project,
  type ProjectMatchResult,
  fetchProjectMatch,
  fetchProjects,
} from "../../lib/api";
import { useAuth } from "../../lib/auth-context";

export default function ProjectsPage() {
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [matches, setMatches] = useState<Record<string, ProjectMatchResult>>({});
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("");

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    }
  }, [authLoading, user, router]);

  useEffect(() => {
    if (!user) return;
    const timeout = setTimeout(() => {
      loadProjects();
    }, 300);
    return () => clearTimeout(timeout);
  }, [user]);

  async function loadProjects() {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchProjects();
      let filtered = data;
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        filtered = filtered.filter(
          (p) =>
            p.name.toLowerCase().includes(query) || p.description?.toLowerCase().includes(query),
        );
      }
      if (statusFilter) {
        filtered = filtered.filter((p) => p.status === statusFilter);
      }
      setProjects(filtered);
      if (user) {
        const matchResults: Record<string, ProjectMatchResult> = {};
        await Promise.all(
          filtered.map(async (p) => {
            try {
              const match = await fetchProjectMatch(p.id);
              matchResults[p.id] = match;
            } catch {
              // Some projects may not have requirements yet
            }
          }),
        );
        setMatches(matchResults);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load projects");
    } finally {
      setLoading(false);
    }
  }

  const getMatchStatus = (projectId: string) => {
    const match = matches[projectId];
    if (!match) return null;
    if (match.eligible) return { label: "Eligible", color: "emerald" };
    if (match.missing.length > 0) return { label: "Missing Capabilities", color: "red" };
    if (match.gaps.length > 0) return { label: "Skill Gaps", color: "amber" };
    return { label: "No Match Data", color: "slate" };
  };

  const statuses = [
    "draft",
    "open",
    "planning",
    "active",
    "paused",
    "completed",
    "cancelled",
    "archived",
  ];

  if (authLoading || loading) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-white text-slate-600">
        <div className="flex items-center space-x-3">
          <div className="w-5 h-5 border-2 border-slate-900 border-t-transparent rounded-full animate-spin" />
          <span className="text-sm font-medium">Loading projects...</span>
        </div>
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
        <Link href="/dashboard" className="text-slate-500 hover:text-slate-700 font-medium text-sm">
          Back to Dashboard
        </Link>
      </header>

      <div className="flex-1 max-w-5xl w-full mx-auto p-6 md:p-10 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-slate-900">Discover Projects</h1>
            <p className="text-slate-500 mt-1 text-sm">
              Browse available projects and see how your capabilities align.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <input
            type="text"
            placeholder="Search projects..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="px-3 py-2 bg-white border border-slate-300 rounded-lg text-sm text-slate-900 focus:outline-none focus:border-slate-900 w-64"
          />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 bg-white border border-slate-300 rounded-lg text-sm text-slate-900 focus:outline-none focus:border-slate-900"
          >
            <option value="">All statuses</option>
            {statuses.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 text-sm">
            {error}
          </div>
        )}

        <div className="border border-slate-200 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-slate-500">Project</th>
                <th className="text-left px-4 py-3 font-medium text-slate-500">Status</th>
                <th className="text-left px-4 py-3 font-medium text-slate-500">Type</th>
                <th className="text-left px-4 py-3 font-medium text-slate-500">Match</th>
                <th className="text-right px-4 py-3 font-medium text-slate-500">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {projects.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-slate-500">
                    No projects available yet.
                  </td>
                </tr>
              ) : (
                projects.map((project) => {
                  const matchStatus = getMatchStatus(project.id);
                  return (
                    <tr key={project.id} className="hover:bg-slate-50">
                      <td className="px-4 py-3">
                        <div className="font-medium text-slate-900">{project.name}</div>
                        <div className="text-slate-500 text-xs mt-0.5 line-clamp-1">
                          {project.description || "No description"}
                        </div>
                      </td>
                      <td className="px-4 py-3">
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
                      </td>
                      <td className="px-4 py-3 text-slate-600">{project.project_type}</td>
                      <td className="px-4 py-3">
                        {matchStatus && (
                          <span
                            className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                              matchStatus.color === "emerald"
                                ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                                : matchStatus.color === "red"
                                  ? "bg-red-50 text-red-700 border border-red-200"
                                  : matchStatus.color === "amber"
                                    ? "bg-amber-50 text-amber-700 border border-amber-200"
                                    : "bg-slate-100 text-slate-600 border border-slate-200"
                            }`}
                          >
                            {matchStatus.label}
                          </span>
                        )}
                        {matches[project.id] && (
                          <span className="ml-2 text-xs text-slate-500 font-mono">
                            {matches[project.id].match_score}%
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <Link
                          href={`/projects/${project.id}`}
                          className="text-slate-900 hover:text-slate-700 text-sm font-medium"
                        >
                          View Details
                        </Link>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  );
}
