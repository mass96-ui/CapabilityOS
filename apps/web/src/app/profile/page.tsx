"use client";

import Link from "next/link";
import type React from "react";
import { useEffect, useState } from "react";
import {
  type LearnerProfile,
  createLearnerProfile,
  fetchLearnerProfile,
  updateLearnerProfile,
} from "../../lib/api";
import { useAuth } from "../../lib/auth-context";

export default function ProfilePage() {
  const { user, isLoading } = useAuth();
  const [profile, setProfile] = useState<LearnerProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [displayName, setDisplayName] = useState("");
  const [headline, setHeadline] = useState("");
  const [bio, setBio] = useState("");
  const [location, setLocation] = useState("");

  useEffect(() => {
    if (!user) return;

    async function load() {
      try {
        const data = await fetchLearnerProfile();
        setProfile(data);
        setDisplayName(data.display_name || "");
        setHeadline(data.headline || "");
        setBio(data.bio || "");
        setLocation(data.location || "");
      } catch {
        // Profile might not exist yet
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [user]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setSaving(true);

    try {
      const payload = {
        display_name: displayName || undefined,
        headline: headline || undefined,
        bio: bio || undefined,
        location: location || undefined,
      };
      if (profile) {
        const updated = await updateLearnerProfile(payload);
        setProfile(updated);
        setSuccess("Profile updated successfully.");
      } else {
        const created = await createLearnerProfile(payload);
        setProfile(created);
        setSuccess("Profile created successfully.");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save profile.");
    } finally {
      setSaving(false);
    }
  };

  if (isLoading || loading) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-300">
        <div className="flex items-center space-x-3">
          <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          <span>Loading profile...</span>
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
            Profile
          </span>
        </div>
      </header>

      <div className="flex-1 max-w-2xl w-full mx-auto p-6 md:p-10">
        <Link
          href="/dashboard"
          className="text-indigo-400 hover:text-indigo-300 text-sm font-medium"
        >
          ← Back to Dashboard
        </Link>

        <h1 className="text-3xl font-extrabold text-white mt-4 mb-8">Learner Profile</h1>

        {error && (
          <div className="mb-6 p-4 bg-red-950/60 border border-red-800 rounded-xl text-red-300 text-sm">
            {error}
          </div>
        )}
        {success && (
          <div className="mb-6 p-4 bg-emerald-950/60 border border-emerald-800 rounded-xl text-emerald-300 text-sm">
            {success}
          </div>
        )}

        <form
          onSubmit={handleSubmit}
          className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 md:p-8 space-y-6"
        >
          <div>
            <label
              htmlFor="display_name"
              className="block text-xs font-semibold text-slate-400 mb-2"
            >
              Display Name
            </label>
            <input
              id="display_name"
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="Alex Morgan"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
            />
          </div>

          <div>
            <label htmlFor="headline" className="block text-xs font-semibold text-slate-400 mb-2">
              Headline
            </label>
            <input
              id="headline"
              type="text"
              value={headline}
              onChange={(e) => setHeadline(e.target.value)}
              placeholder="Full-stack engineer | CapabilityOS learner"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
            />
          </div>

          <div>
            <label htmlFor="bio" className="block text-xs font-semibold text-slate-400 mb-2">
              Bio
            </label>
            <textarea
              id="bio"
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              placeholder="Tell us about your experience and goals..."
              rows={4}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
            />
          </div>

          <div>
            <label htmlFor="location" className="block text-xs font-semibold text-slate-400 mb-2">
              Location
            </label>
            <input
              id="location"
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="City, Country"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
            />
          </div>

          <button
            type="submit"
            disabled={saving}
            className="w-full py-3.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl disabled:opacity-50 transition-all"
          >
            {saving ? "Saving..." : "Save Profile"}
          </button>
        </form>
      </div>
    </main>
  );
}
