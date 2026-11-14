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
import {
  formatDashboardDate,
  getDashboardRecords,
  getSafeAssessmentStatus,
  getSafeCapabilityScore,
  getSafePercentage,
  getSafeProficiency,
  getSafeText,
} from "./dashboard-data";

export default function DashboardPage() {
  const router = useRouter();
  const { user, isLoading: authLoading, logout } = useAuth();
  const [capabilities, setCapabilities] = useState<UserCapability[] | null>(null);
  const [passport, setPassport] = useState<EngineeringPassport | null>(null);
  const [loadingData, setLoadingData] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    if (!authLoading && !user) router.replace("/login");
  }, [authLoading, user, router]);

  useEffect(() => {
    if (!user) return;
    let cancelled = false;
    setLoadingData(true);
    setCapabilities(null);
    setPassport(null);
    setHasError(false);

    Promise.allSettled([fetchUserCapabilities(user.id), fetchPassport()]).then(([caps, pass]) => {
      if (cancelled) return;
      if (caps.status === "fulfilled" && Array.isArray(caps.value)) setCapabilities(caps.value);
      else setHasError(true);
      if (pass.status === "fulfilled" && pass.value != null) setPassport(pass.value);
      else setHasError(true);
      setLoadingData(false);
    });

    return () => {
      cancelled = true;
    };
  }, [user, reloadKey]);

  const handleLogout = () => {
    logout();
    router.replace("/login");
  };

  if (authLoading || (user && loadingData)) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-300 px-4" aria-busy="true" aria-live="polite">
        <div className="flex items-center gap-3">
          <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          <span>Loading learner workspace...</span>
        </div>
      </main>
    );
  }
  if (!user) return null;

  const passportCapabilities = getDashboardRecords<EngineeringPassport["capabilities"][number]>(passport?.capabilities);
  const assessmentHistory = getDashboardRecords<EngineeringPassport["assessment_history"][number]>(passport?.assessment_history);
  const projects = getDashboardRecords<EngineeringPassport["project_experience"][number]>(passport?.project_experience);
  const recentAssessments = assessmentHistory.slice(0, 3);
  const displayName = getSafeText(user.first_name) ?? getSafeText(user.username) ?? "learner";

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md px-4 sm:px-6 py-4 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Link href="/" className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-300 bg-clip-text text-transparent">CapabilityOS</Link>
          <span className="text-xs px-2.5 py-1 bg-indigo-950 border border-indigo-800 text-indigo-300 rounded-full font-medium">Learner Workspace</span>
        </div>
        <nav aria-label="Learner navigation" className="flex flex-wrap items-center gap-4 text-sm">
          <Link href="/capabilities" className="text-slate-300 hover:text-white">Capabilities</Link>
          <Link href="/assessments" className="text-slate-300 hover:text-white">Assessments</Link>
          <Link href="/passport" className="text-slate-300 hover:text-white">Passport</Link>
          <button type="button" onClick={handleLogout} className="px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-sm font-medium rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-400">Sign out</button>
        </nav>
      </header>

      <div className="flex-1 max-w-5xl w-full mx-auto p-4 sm:p-6 md:p-10 space-y-6 sm:space-y-8">
        <section className="bg-gradient-to-r from-indigo-900/40 via-slate-900 to-slate-900 border border-indigo-900/50 rounded-2xl p-6 sm:p-8 shadow-xl">
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white">Welcome back, {displayName}!</h1>
          <p className="text-slate-400 mt-2 max-w-2xl">Track your capability records, review assessment history, and build your Engineering Passport.</p>
        </section>

        {hasError && <div role="alert" className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 bg-amber-950/50 border border-amber-800 rounded-xl text-amber-200 text-sm"><span>Some dashboard information is unavailable. Your displayed information may be incomplete.</span><button type="button" onClick={() => setReloadKey((key) => key + 1)} className="self-start sm:self-auto rounded-lg border border-amber-700 px-3 py-2 hover:bg-amber-900/50 focus:outline-none focus:ring-2 focus:ring-amber-300">Retry</button></div>}

        <section aria-labelledby="capabilities-heading" className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 sm:p-6">
          <div className="flex flex-wrap items-center justify-between gap-3 mb-4"><h2 id="capabilities-heading" className="text-xl font-semibold text-white">Capability progress</h2><Link href="/capabilities" className="text-sm font-medium text-indigo-300 hover:text-indigo-200">View capabilities →</Link></div>
          {capabilities === null && passportCapabilities.length === 0 ? <p className="text-sm text-slate-400">Capability information is unavailable or has not been added yet.</p> : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="rounded-xl bg-slate-950/50 border border-slate-800 p-4"><p className="text-sm text-slate-400">Learner capability records</p><p className="mt-1 text-2xl font-bold text-white">{capabilities?.length ?? "—"}</p></div>
              {passportCapabilities.length === 0 ? <div className="rounded-xl bg-slate-950/50 border border-slate-800 p-4 text-sm text-slate-400">No proficiency details are present in your Engineering Passport.</div> : <div className="space-y-4 rounded-xl bg-slate-950/50 border border-slate-800 p-4"><p className="text-sm text-slate-400">Engineering Passport proficiency (separate source)</p>{passportCapabilities.slice(0, 3).map((capability, index) => {
                const name = getSafeText(capability?.name) ?? "Capability name unavailable";
                const level = getSafeProficiency(capability?.proficiency_level);
                const score = getSafeCapabilityScore(capability?.score);
                const date = formatDashboardDate(capability?.last_assessed_at);
                return <div key={`${getSafeText(capability?.id) ?? "capability"}-${index}`}><div className="flex justify-between gap-2 text-sm"><span className="text-slate-200">{name}</span><span className="text-indigo-300">{level === null ? "Level unavailable" : `Level ${level}/4`}</span></div>{level !== null && <div className="mt-2 h-2 rounded-full bg-slate-800" role="progressbar" aria-label={`${name} proficiency`} aria-valuemin={1} aria-valuemax={4} aria-valuenow={level}><div className="h-2 rounded-full bg-indigo-500" style={{ width: `${(level / 4) * 100}%` }} /></div>}<p className="mt-1 text-xs text-slate-500">{score === null ? "Score unavailable" : `Score ${score.toFixed(1)} / 100`}{date ? ` · Assessed ${date}` : ""}</p></div>;
              })}</div>}
            </div>
          )}
        </section>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <section aria-labelledby="activity-heading" className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 sm:p-6"><div className="flex justify-between gap-3 mb-4"><h2 id="activity-heading" className="text-lg font-semibold text-white">Assessment history</h2><Link href="/assessments" className="text-sm text-indigo-300 hover:text-indigo-200">Explore →</Link></div>{recentAssessments.length === 0 ? <p className="text-sm text-slate-400">No assessment history is available in your passport yet.</p> : <ul className="divide-y divide-slate-800">{recentAssessments.map((item, index) => {const title = getSafeText(item?.assessment_title) ?? "Assessment title unavailable"; const percentage = getSafePercentage(item?.percentage); const date = formatDashboardDate(item?.submitted_at); return <li key={`${getSafeText(item?.attempt_id) ?? getSafeText(item?.assessment_id) ?? "assessment"}-${index}`} className="py-3"><p className="font-medium text-slate-200 break-words">{title}</p><p className="mt-1 text-xs text-slate-400">{getSafeAssessmentStatus(item?.status)}{date ? ` · ${date}` : ""}{percentage !== null ? ` · ${percentage.toFixed(0)}%` : ""}</p></li>;})}</ul>}</section>
          <section aria-labelledby="passport-heading" className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 sm:p-6"><h2 id="passport-heading" className="text-lg font-semibold text-white">Engineering Passport</h2><p className="text-sm text-slate-400 mt-2">{passport ? `${passportCapabilities.length} passport capability records · ${projects.length} project experiences` : "Passport details are unavailable."}</p><Link href="/passport" className="inline-flex mt-4 text-sm font-semibold text-indigo-300 hover:text-indigo-200">View Engineering Passport →</Link></section>
        </div>

        <nav aria-label="Next steps" className="grid grid-cols-1 sm:grid-cols-3 gap-4"><Link href="/assessments" className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 hover:border-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"><h3 className="font-semibold text-white">Find an assessment</h3><p className="mt-1 text-sm text-slate-400">Add evidence to your learner profile.</p></Link><Link href="/capabilities" className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 hover:border-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"><h3 className="font-semibold text-white">Review capabilities</h3><p className="mt-1 text-sm text-slate-400">Explore your proficiency details.</p></Link><Link href="/projects" className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 hover:border-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"><h3 className="font-semibold text-white">Discover projects</h3><p className="mt-1 text-sm text-slate-400">Browse projects and capability matches.</p></Link></nav>
      </div>
    </main>
  );
}
