"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import type React from "react";
import { useState } from "react";
import { useAuth } from "../../lib/auth-context";

export default function VerifyEmailPage() {
  const router = useRouter();
  const { verifyEmail, resendVerification } = useAuth();
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [resending, setResending] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setSubmitting(true);

    try {
      await verifyEmail(email, otp);
      router.push("/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Verification failed. Please check your OTP.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleResend = async () => {
    if (!email) {
      setError("Please enter your email address to resend the OTP.");
      return;
    }
    setError(null);
    setSuccess(null);
    setResending(true);

    try {
      await resendVerification(email);
      setSuccess("A new verification OTP has been sent to your email.");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to resend OTP.");
    } finally {
      setResending(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950">
      <div className="w-full max-w-md bg-slate-900/80 backdrop-blur-md border border-slate-800 rounded-2xl p-8 shadow-2xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-blue-400 to-indigo-300 bg-clip-text text-transparent">
            CapabilityOS
          </h1>
          <p className="text-slate-400 text-sm mt-2">Verify your email address</p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-950/60 border border-red-800 rounded-xl text-red-300 text-sm flex items-start space-x-2">
            <span className="font-semibold">Error:</span>
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="mb-6 p-4 bg-emerald-950/60 border border-emerald-800 rounded-xl text-emerald-300 text-sm">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label
              htmlFor="email"
              className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2"
            >
              Email Address
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="learner@capabilityos.dev"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
            />
          </div>

          <div>
            <label
              htmlFor="otp"
              className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2"
            >
              Verification OTP
            </label>
            <input
              id="otp"
              type="text"
              required
              maxLength={6}
              pattern="\d{6}"
              value={otp}
              onChange={(e) => setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))}
              placeholder="123456"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all text-center text-2xl tracking-widest"
            />
            <p className="text-xs text-slate-500 mt-1">
              Enter the 6-digit code sent to your email.
            </p>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full py-3.5 px-4 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white font-semibold rounded-xl shadow-lg shadow-indigo-600/20 disabled:opacity-50 transition-all cursor-pointer"
          >
            {submitting ? "Verifying..." : "Verify Email"}
          </button>
        </form>

        <div className="mt-6 space-y-3">
          <button
            type="button"
            onClick={handleResend}
            disabled={resending}
            className="w-full py-2.5 text-indigo-400 hover:text-indigo-300 text-sm font-semibold disabled:opacity-50 transition-all cursor-pointer"
          >
            {resending ? "Sending..." : "Resend OTP"}
          </button>

          <div className="text-center text-sm text-slate-400">
            Already verified?{" "}
            <Link
              href="/login"
              className="text-indigo-400 hover:text-indigo-300 font-semibold underline underline-offset-4"
            >
              Sign In
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
