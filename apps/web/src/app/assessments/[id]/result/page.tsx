"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import React, { useEffect, useState } from "react";
import {
  type AssessmentAnswer,
  type AssessmentAttemptResult,
  fetchAttemptResult,
} from "../../../../lib/api";
import { useAuth } from "../../../../lib/auth-context";

export default function AssessmentResultPage({ params }: { params: { id: string } }) {
  const searchParams = useSearchParams();
  const attemptId = searchParams.get("attempt");
  const { user, isLoading } = useAuth();
  const [result, setResult] = useState<AssessmentAttemptResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!attemptId) return;

    async function load() {
      if (!attemptId) return;
      try {
        const data = await fetchAttemptResult(attemptId);
        setResult(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load result.");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [attemptId]);

  if (isLoading || loading) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-300">
        <div className="flex items-center space-x-3">
          <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          <span>Loading result...</span>
        </div>
      </main>
    );
  }

  if (!user || !result) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-300">
        <div className="text-center">
          <p className="text-lg">{error || "Result not found."}</p>
          <Link
            href="/assessments"
            className="mt-4 inline-block text-indigo-400 hover:text-indigo-300"
          >
            ← Back to Assessments
          </Link>
        </div>
      </main>
    );
  }

  const percentage = result.attempt.percentage != null ? result.attempt.percentage : 0;

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
            Result
          </span>
        </div>
      </header>

      <div className="flex-1 max-w-4xl w-full mx-auto p-6 md:p-10 space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-extrabold text-white">Assessment Complete</h1>
          <p className="text-slate-400 mt-2">Here is how you performed.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 text-center">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Score
            </span>
            <p className="text-4xl font-extrabold text-white mt-2">
              {result.attempt.score != null ? result.attempt.score.toFixed(1) : "—"}
            </p>
            <p className="text-sm text-slate-400 mt-1">
              / {result.attempt.max_score != null ? result.attempt.max_score.toFixed(1) : "—"}
            </p>
          </div>
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 text-center">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Percentage
            </span>
            <p className="text-4xl font-extrabold text-indigo-300 mt-2">{percentage.toFixed(0)}%</p>
          </div>
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 text-center">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Correct
            </span>
            <p className="text-4xl font-extrabold text-emerald-300 mt-2">
              {result.attempt.correct_count}/{result.attempt.question_count}
            </p>
          </div>
        </div>

        {result.capability && (
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h2 className="text-lg font-semibold text-slate-200">Capability Update</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <span className="text-xs text-slate-500 uppercase tracking-wider">Score</span>
                <p className="text-xl font-semibold text-white">
                  {result.capability.score.toFixed(1)}
                </p>
              </div>
              <div>
                <span className="text-xs text-slate-500 uppercase tracking-wider">Confidence</span>
                <p className="text-xl font-semibold text-white">
                  {(result.capability.confidence * 100).toFixed(0)}%
                </p>
              </div>
              <div>
                <span className="text-xs text-slate-500 uppercase tracking-wider">Proficiency</span>
                <p className="text-xl font-semibold text-white">
                  {result.capability.proficiency_level}/5
                </p>
              </div>
              <div>
                <span className="text-xs text-slate-500 uppercase tracking-wider">Verified</span>
                <p className="text-xl font-semibold text-white">
                  {result.capability.verified ? "Yes" : "No"}
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4">
          <h2 className="text-lg font-semibold text-slate-200">Your Answers</h2>
          <div className="space-y-3">
            {result.answers.map((answer: AssessmentAnswer, idx: number) => (
              <div
                key={answer.id}
                className="flex items-center justify-between py-3 border-b border-slate-800 last:border-0"
              >
                <div className="flex items-center space-x-3">
                  <span className="text-sm font-semibold text-slate-400">Q{idx + 1}</span>
                  <span className="text-sm text-slate-300">{answer.selected_answer}</span>
                </div>
                <div className="flex items-center space-x-3">
                  <span className="text-sm text-slate-400">{answer.points_earned} pts</span>
                  <span
                    className={`text-xs px-2 py-1 rounded-full ${
                      answer.is_correct
                        ? "bg-emerald-950 border border-emerald-800 text-emerald-300"
                        : "bg-red-950 border border-red-800 text-red-300"
                    }`}
                  >
                    {answer.is_correct ? "Correct" : "Incorrect"}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="flex items-center justify-between">
          <Link href="/assessments" className="text-indigo-400 hover:text-indigo-300 font-medium">
            ← Back to Assessments
          </Link>
          <Link href="/capabilities" className="text-indigo-400 hover:text-indigo-300 font-medium">
            View Capabilities →
          </Link>
        </div>
      </div>
    </main>
  );
}
