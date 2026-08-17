"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import React, { useEffect, useState } from "react";
import {
  type Assessment,
  type AssessmentQuestion,
  createAssessmentAttempt,
  fetchAssessmentById,
  fetchAssessmentQuestions,
  submitAnswer,
  submitAssessmentAttempt,
} from "../../../../lib/api";
import { useAuth } from "../../../../lib/auth-context";

export default function AssessmentAttemptPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuth();
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [questions, setQuestions] = useState<AssessmentQuestion[]>([]);
  const [attemptId, setAttemptId] = useState<string | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Map<string, string>>(new Map());
  const [saving, setSaving] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [started, setStarted] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  useEffect(() => {
    if (!user) return;

    async function init() {
      try {
        const [assessmentData, questionsData] = await Promise.all([
          fetchAssessmentById(params.id),
          fetchAssessmentQuestions(params.id),
        ]);
        setAssessment(assessmentData);
        const sorted = questionsData.sort(
          (a: AssessmentQuestion, b: AssessmentQuestion) => a.question_order - b.question_order,
        );
        setQuestions(sorted);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load assessment.");
      } finally {
        setLoading(false);
      }
    }

    init();
  }, [user, params.id]);

  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (started && answers.size > 0 && !submitting) {
        e.preventDefault();
        e.returnValue = "";
      }
    };
    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, [started, answers.size, submitting]);

  const startAttempt = async () => {
    if (!user || !assessment) return;
    try {
      const attempt = await createAssessmentAttempt(user.id, assessment.id);
      setAttemptId(attempt.id);
      setStarted(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start assessment.");
    }
  };

  const handleAnswer = async (questionId: string, selectedAnswer: string) => {
    if (!attemptId) return;
    setAnswers((prev) => new Map(prev).set(questionId, selectedAnswer));
    try {
      await submitAnswer(attemptId, questionId, selectedAnswer);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to save answer.";
      if (message.includes("already been answered")) {
        setAnswers((prev) => new Map(prev).set(questionId, selectedAnswer));
      } else {
        setError(message);
      }
    }
  };

  const handleSaveTextAnswer = async () => {
    if (!currentQuestion || !attemptId) return;
    const currentAnswer = answers.get(currentQuestion.id) || "";
    setSaving(true);
    try {
      await submitAnswer(attemptId, currentQuestion.id, currentAnswer);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to save answer.";
      if (!message.includes("already been answered")) {
        setError(message);
      }
    } finally {
      setSaving(false);
    }
  };

  const handleSubmit = async () => {
    if (!attemptId) return;
    setShowConfirm(true);
  };

  const confirmSubmit = async () => {
    if (!attemptId) return;
    setShowConfirm(false);
    setSubmitting(true);
    try {
      await submitAssessmentAttempt(attemptId);
      router.push(`/assessments/${params.id}/result?attempt=${attemptId}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit assessment.");
      setSubmitting(false);
    }
  };

  if (authLoading || loading) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-300">
        <div className="flex items-center space-x-3">
          <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          <span>Loading assessment...</span>
        </div>
      </main>
    );
  }

  if (!user || !assessment) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-300">
        <div className="text-center">
          <p className="text-lg">{error || "Assessment not found."}</p>
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

  if (!started) {
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
              Assessment
            </span>
          </div>
        </header>

        <div className="flex-1 max-w-3xl w-full mx-auto p-6 md:p-10">
          <Link
            href="/assessments"
            className="text-indigo-400 hover:text-indigo-300 text-sm font-medium"
          >
            ← Back to Assessments
          </Link>
          <div className="mt-8 bg-slate-900/60 border border-slate-800 rounded-2xl p-8 space-y-6">
            <div>
              <h1 className="text-3xl font-extrabold text-white">{assessment.title}</h1>
              <p className="text-slate-400 mt-3">{assessment.description}</p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-4">
                <span className="text-xs text-slate-500 uppercase tracking-wider">Questions</span>
                <p className="text-xl font-semibold text-white mt-1">{questions.length}</p>
              </div>
              <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-4">
                <span className="text-xs text-slate-500 uppercase tracking-wider">Difficulty</span>
                <p className="text-xl font-semibold text-white mt-1 capitalize">
                  {assessment.difficulty}
                </p>
              </div>
            </div>
            {error && (
              <div className="p-4 bg-red-950/60 border border-red-800 rounded-xl text-red-300 text-sm">
                {error}
              </div>
            )}
            <button
              type="button"
              onClick={startAttempt}
              className="w-full py-3.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl transition-all"
            >
              Start Assessment
            </button>
          </div>
        </div>
      </main>
    );
  }

  const currentQuestion = questions[currentIndex];
  const selectedAnswer = currentQuestion ? answers.get(currentQuestion.id) : undefined;
  const parsedOptions = currentQuestion?.options_json
    ? JSON.parse(currentQuestion.options_json)
    : null;

  if (!currentQuestion) {
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
          </div>
        </header>
        <div className="flex-1 max-w-3xl w-full mx-auto p-6 md:p-10">
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-12 text-center">
            <p className="text-slate-400 text-lg">No questions available for this assessment.</p>
            <Link
              href="/assessments"
              className="mt-4 inline-block text-indigo-400 hover:text-indigo-300"
            >
              ← Back to Assessments
            </Link>
          </div>
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
            Question {currentIndex + 1}/{questions.length}
          </span>
        </div>
        <div className="text-sm text-slate-400">
          Answered: {answers.size}/{questions.length}
        </div>
      </header>

      <div className="flex-1 max-w-3xl w-full mx-auto p-6 md:p-10">
        {error && (
          <div className="mb-6 p-4 bg-red-950/60 border border-red-800 rounded-xl text-red-300 text-sm">
            {error}
          </div>
        )}

        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 md:p-8 space-y-6">
          <div>
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Question {currentQuestion.question_order}
            </span>
            <h2 className="text-xl font-semibold text-white mt-2">
              {currentQuestion.question_text}
            </h2>
            <span className="inline-block mt-2 text-xs px-2 py-1 bg-slate-800 border border-slate-700 text-slate-300 rounded-full">
              {currentQuestion.points} points
            </span>
          </div>

          {parsedOptions && Array.isArray(parsedOptions) ? (
            <div className="space-y-3">
              {parsedOptions.map((option: string, idx: number) => (
                <button
                  key={option}
                  type="button"
                  onClick={() => handleAnswer(currentQuestion.id, option)}
                  className={`w-full text-left p-4 rounded-xl border transition-all ${
                    selectedAnswer === option
                      ? "bg-indigo-950 border-indigo-700 text-indigo-200"
                      : "bg-slate-950 border-slate-800 text-slate-300 hover:border-slate-700"
                  }`}
                >
                  <span className="font-semibold mr-2">{String.fromCharCode(65 + idx)}.</span>
                  {option}
                </button>
              ))}
            </div>
          ) : (
            <div className="space-y-3">
              <label
                htmlFor="text-answer"
                className="block text-xs font-semibold text-slate-400 mb-2"
              >
                Your Answer
              </label>
              <input
                id="text-answer"
                type="text"
                value={selectedAnswer || ""}
                onChange={(e) =>
                  setAnswers((prev) => new Map(prev).set(currentQuestion.id, e.target.value))
                }
                placeholder="Type your answer..."
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              />
              <button
                type="button"
                onClick={handleSaveTextAnswer}
                disabled={saving}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium rounded-xl disabled:opacity-50 transition-all"
              >
                {saving ? "Saving..." : "Save Answer"}
              </button>
            </div>
          )}

          <div className="flex items-center justify-between pt-4">
            <button
              type="button"
              onClick={() => setCurrentIndex((i) => Math.max(0, i - 1))}
              disabled={currentIndex === 0}
              className="px-6 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium rounded-xl disabled:opacity-50 transition-all"
            >
              Previous
            </button>
            {currentIndex < questions.length - 1 ? (
              <button
                type="button"
                onClick={() => setCurrentIndex((i) => i + 1)}
                className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl transition-all"
              >
                Next
              </button>
            ) : (
              <button
                type="button"
                onClick={handleSubmit}
                disabled={submitting || answers.size === 0}
                className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-xl disabled:opacity-50 transition-all"
              >
                {submitting ? "Submitting..." : "Submit Assessment"}
              </button>
            )}
          </div>
        </div>
      </div>

      {showConfirm && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-md w-full shadow-2xl">
            <h3 className="text-lg font-semibold text-white mb-2">Submit Assessment?</h3>
            <p className="text-slate-400 text-sm mb-6">
              You have answered {answers.size} of {questions.length} questions. Once submitted, you
              cannot change your answers.
            </p>
            <div className="flex items-center justify-end space-x-3">
              <button
                type="button"
                onClick={() => setShowConfirm(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium rounded-xl transition-all"
              >
                Continue Editing
              </button>
              <button
                type="button"
                onClick={confirmSubmit}
                disabled={submitting}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-xl disabled:opacity-50 transition-all"
              >
                {submitting ? "Submitting..." : "Confirm Submit"}
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
