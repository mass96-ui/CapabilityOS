"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import type React from "react";
import { useState } from "react";
import { useAuth } from "../../lib/auth-context";

export default function RegisterPage() {
  const router = useRouter();
  const { register } = useAuth();

  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setSubmitting(true);

    try {
      await register({
        first_name: firstName,
        last_name: lastName,
        username,
        email,
        password,
        confirm_password: confirmPassword,
      });
      router.push("/login");
    } catch (err: unknown) {
      setError(
        err instanceof Error ? err.message : "Registration failed. Please check your details.",
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950">
      <div className="w-full max-w-lg bg-slate-900/80 backdrop-blur-md border border-slate-800 rounded-2xl p-8 shadow-2xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-blue-400 to-indigo-300 bg-clip-text text-transparent">
            CapabilityOS
          </h1>
          <p className="text-slate-400 text-sm mt-2">
            Learner Registration â€” Create your practical capability account
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-950/60 border border-red-800 rounded-xl text-red-300 text-sm flex items-start space-x-2">
            <span className="font-semibold">Error:</span>
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label
                htmlFor="first_name"
                className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5"
              >
                First Name
              </label>
              <input
                type="text"
                required
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                placeholder="Alex"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              />
            </div>
            <div>
              <label
                htmlFor="last_name"
                className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5"
              >
                Last Name
              </label>
              <input
                type="text"
                required
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                placeholder="Morgan"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              />
            </div>
          </div>

          <div>
            <label
              htmlFor="username"
              className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5"
            >
              Username
            </label>
            <input
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="alexm"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
            />
          </div>

          <div>
            <label
              htmlFor="email"
              className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5"
            >
              Email Address
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="alex@capabilityos.dev"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label
                htmlFor="password"
                className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5"
              >
                Password
              </label>
              <input
                type="password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="â€¢â€¢â€¢â€¢â€¢â€¢â€¢â€¢"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              />
            </div>
            <div>
              <label
                htmlFor="confirm_password"
                className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5"
              >
                Confirm Password
              </label>
              <input
                type="password"
                required
                minLength={8}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="â€¢â€¢â€¢â€¢â€¢â€¢â€¢â€¢"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full mt-2 py-3.5 px-4 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white font-semibold rounded-xl shadow-lg shadow-indigo-600/20 disabled:opacity-50 transition-all cursor-pointer"
          >
            {submitting ? "Creating Account..." : "Register Account"}
          </button>
        </form>

        <div className="mt-8 text-center text-sm text-slate-400">
          Already have an account?{" "}
          <Link
            href="/login"
            className="text-indigo-400 hover:text-indigo-300 font-semibold underline underline-offset-4"
          >
            Sign In
          </Link>
        </div>
      </div>
    </main>
  );
}
