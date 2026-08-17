"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import type React from "react";
import { useEffect, useState } from "react";
import {
  type Project,
  type ProjectMatchesResponse,
  type ProjectRequirement,
  createProject,
  createProjectRequirement,
  deleteProject,
  deleteProjectRequirement,
  fetchCapabilities,
  fetchOwnerProjects,
  fetchProjectMatches,
  fetchProjectRequirements,
  fetchProjects,
  updateProject,
  updateProjectRequirement,
} from "../../../lib/api";
import { useAuth } from "../../../lib/auth-context";

type ModalState = {
  mode: "create" | "edit" | "delete" | "requirements" | "matches" | null;
  project?: Project;
};

type Toast = {
  id: string;
  message: string;
  type: "success" | "error";
};

export default function ManagerDashboardPage() {
  const router = useRouter();
  const { user, isLoading: authLoading, logout } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState<ModalState>({ mode: null });
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    status: "open",
    project_type: "real_world",
  });
  const [requirements, setRequirements] = useState<ProjectRequirement[]>([]);
  const [capabilities, setCapabilities] = useState<{ id: string; name: string }[]>([]);
  const [reqForm, setReqForm] = useState({
    capability_id: "",
    description: "",
    minimum_proficiency_level: 1,
    importance: 1.0,
    required: true,
  });
  const [matches, setMatches] = useState<ProjectMatchesResponse | null>(null);
  const [matchesLoading, setMatchesLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("");

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    }
    if (user && user.role !== "manager" && !user.is_superuser) {
      router.push("/dashboard");
    }
  }, [authLoading, user, router]);

  useEffect(() => {
    if (!user) return;
    loadProjects();
    loadCapabilities();
  }, [user]);

  useEffect(() => {
    if (!user) return;
    const timeout = setTimeout(() => {
      loadProjects();
    }, 300);
    return () => clearTimeout(timeout);
  }, [user]);

  function showToast(message: string, type: Toast["type"] = "success") {
    const id = crypto.randomUUID();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  }

  async function loadProjects() {
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      const data = await fetchOwnerProjects(user.id);
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
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load projects");
    } finally {
      setLoading(false);
    }
  }

  async function loadCapabilities() {
    try {
      const data = await fetchCapabilities();
      setCapabilities(data.map((c) => ({ id: c.id, name: c.name })));
    } catch {
      // capabilities may not be available
    }
  }

  async function handleCreateProject(e: React.FormEvent) {
    e.preventDefault();
    if (!user) return;
    setSubmitting(true);
    setError(null);
    try {
      await createProject({
        ...formData,
        owner_id: user.id,
      });
      setFormData({ name: "", description: "", status: "open", project_type: "real_world" });
      setModal({ mode: null });
      await loadProjects();
      showToast("Project created successfully");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create project");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleUpdateProject(e: React.FormEvent) {
    e.preventDefault();
    if (!modal.project) return;
    setSubmitting(true);
    setError(null);
    try {
      await updateProject(modal.project.id, formData);
      setModal({ mode: null });
      await loadProjects();
      showToast("Project updated successfully");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update project");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDeleteProject() {
    if (!modal.project) return;
    setSubmitting(true);
    setError(null);
    try {
      await deleteProject(modal.project.id);
      setModal({ mode: null });
      await loadProjects();
      showToast("Project deleted successfully");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete project");
    } finally {
      setSubmitting(false);
    }
  }

  async function loadRequirements(projectId: string) {
    try {
      const data = await fetchProjectRequirements(projectId);
      setRequirements(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load requirements");
    }
  }

  async function handleCreateRequirement(e: React.FormEvent) {
    e.preventDefault();
    if (!modal.project) return;
    setSubmitting(true);
    setError(null);
    try {
      await createProjectRequirement(modal.project.id, {
        project_id: modal.project.id,
        capability_id: reqForm.capability_id,
        description: reqForm.description || undefined,
        minimum_proficiency_level: reqForm.minimum_proficiency_level,
        importance: reqForm.importance,
        required: reqForm.required,
      });
      setReqForm({
        capability_id: "",
        description: "",
        minimum_proficiency_level: 1,
        importance: 1.0,
        required: true,
      });
      await loadRequirements(modal.project.id);
      showToast("Requirement added");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create requirement");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleUpdateRequirement(req: ProjectRequirement) {
    setSubmitting(true);
    setError(null);
    try {
      await updateProjectRequirement(req.id, {
        description: req.description || undefined,
        minimum_proficiency_level: req.minimum_proficiency_level,
        importance: req.importance,
        required: req.required,
      });
      if (modal.project) {
        await loadRequirements(modal.project.id);
      }
      showToast("Requirement updated");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update requirement");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDeleteRequirement(reqId: string) {
    setSubmitting(true);
    setError(null);
    try {
      await deleteProjectRequirement(reqId);
      if (modal.project) {
        await loadRequirements(modal.project.id);
      }
      showToast("Requirement deleted");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete requirement");
    } finally {
      setSubmitting(false);
    }
  }

  async function loadMatches(projectId: string) {
    setMatchesLoading(true);
    setMatches(null);
    try {
      const data = await fetchProjectMatches(projectId);
      setMatches(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load matches");
    } finally {
      setMatchesLoading(false);
    }
  }

  function openModal(mode: ModalState["mode"], project?: Project) {
    setModal({ mode, project });
    if (mode === "edit" && project) {
      setFormData({
        name: project.name,
        description: project.description || "",
        status: project.status,
        project_type: project.project_type,
      });
    }
    if (mode === "create") {
      setFormData({ name: "", description: "", status: "open", project_type: "real_world" });
    }
    if (mode === "requirements" && project) {
      loadRequirements(project.id);
      setReqForm({
        capability_id: "",
        description: "",
        minimum_proficiency_level: 1,
        importance: 1.0,
        required: true,
      });
    }
    if (mode === "matches" && project) {
      loadMatches(project.id);
    }
    setError(null);
  }

  const handleLogout = () => {
    logout();
    router.push("/login");
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
          <span className="text-sm font-medium">Loading manager workspace...</span>
        </div>
      </main>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <main className="min-h-screen bg-white text-slate-900 flex flex-col">
      <header className="border-b border-slate-200 bg-white px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Link href="/" className="text-lg font-semibold text-slate-900">
            CapabilityOS
          </Link>
          <span className="text-xs px-2.5 py-1 bg-slate-100 border border-slate-200 text-slate-600 rounded-full font-medium">
            Manager
          </span>
        </div>
        <button
          type="button"
          onClick={handleLogout}
          className="px-4 py-2 bg-white border border-slate-300 hover:border-slate-400 text-slate-700 text-sm font-medium rounded-lg transition-all cursor-pointer"
        >
          Sign Out
        </button>
      </header>

      <div className="flex-1 max-w-6xl w-full mx-auto p-6 md:p-10 space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-slate-900">Projects</h1>
            <p className="text-slate-500 mt-1 text-sm">
              Manage your projects and discover matching candidates.
            </p>
          </div>
          <button
            type="button"
            onClick={() => openModal("create")}
            className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white text-sm font-medium rounded-lg transition-all"
          >
            + New Project
          </button>
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

        {toasts.length > 0 && (
          <div className="fixed bottom-4 right-4 z-50 space-y-2">
            {toasts.map((toast) => (
              <div
                key={toast.id}
                className={`px-4 py-3 rounded-lg text-sm font-medium shadow-lg ${
                  toast.type === "success" ? "bg-slate-900 text-white" : "bg-red-600 text-white"
                }`}
              >
                {toast.message}
              </div>
            ))}
          </div>
        )}

        <div className="border border-slate-200 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-slate-500">Name</th>
                <th className="text-left px-4 py-3 font-medium text-slate-500">Status</th>
                <th className="text-left px-4 py-3 font-medium text-slate-500">Type</th>
                <th className="text-right px-4 py-3 font-medium text-slate-500">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {projects.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-4 py-8 text-center text-slate-500">
                    No projects yet. Create your first project to get started.
                  </td>
                </tr>
              ) : (
                projects.map((project) => (
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
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          type="button"
                          onClick={() => openModal("requirements", project)}
                          className="px-2.5 py-1.5 bg-white border border-slate-300 hover:border-slate-400 text-slate-700 text-xs font-medium rounded-md transition-all"
                        >
                          Requirements
                        </button>
                        <button
                          type="button"
                          onClick={() => openModal("matches", project)}
                          className="px-2.5 py-1.5 bg-white border border-slate-300 hover:border-slate-400 text-slate-700 text-xs font-medium rounded-md transition-all"
                        >
                          Matches
                        </button>
                        <button
                          type="button"
                          onClick={() => openModal("edit", project)}
                          className="px-2.5 py-1.5 bg-white border border-slate-300 hover:border-slate-400 text-slate-700 text-xs font-medium rounded-md transition-all"
                        >
                          Edit
                        </button>
                        <button
                          type="button"
                          onClick={() => openModal("delete", project)}
                          className="px-2.5 py-1.5 bg-white border border-red-300 hover:border-red-400 text-red-600 text-xs font-medium rounded-md transition-all"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {modal.mode === "create" && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white border border-slate-200 rounded-xl p-6 w-full max-w-lg shadow-2xl">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-slate-900">Create Project</h3>
              <button
                type="button"
                onClick={() => setModal({ mode: null })}
                className="text-slate-400 hover:text-slate-600 text-xl leading-none"
              >
                &times;
              </button>
            </div>
            <form onSubmit={handleCreateProject} className="space-y-4">
              <div>
                <label
                  htmlFor="create-project-name"
                  className="block text-sm font-medium text-slate-700 mb-1"
                >
                  Name
                </label>
                <input
                  id="create-project-name"
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-slate-900 focus:outline-none focus:border-slate-900 text-sm"
                />
              </div>
              <div>
                <label
                  htmlFor="create-project-description"
                  className="block text-sm font-medium text-slate-700 mb-1"
                >
                  Description
                </label>
                <textarea
                  id="create-project-description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-slate-900 focus:outline-none focus:border-slate-900 text-sm"
                  rows={3}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label
                    htmlFor="create-project-status"
                    className="block text-sm font-medium text-slate-700 mb-1"
                  >
                    Status
                  </label>
                  <select
                    id="create-project-status"
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                    className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-slate-900 focus:outline-none focus:border-slate-900 text-sm"
                  >
                    {statuses.map((s) => (
                      <option key={s} value={s}>
                        {s}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label
                    htmlFor="create-project-type"
                    className="block text-sm font-medium text-slate-700 mb-1"
                  >
                    Type
                  </label>
                  <select
                    id="create-project-type"
                    value={formData.project_type}
                    onChange={(e) => setFormData({ ...formData, project_type: e.target.value })}
                    className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-slate-900 focus:outline-none focus:border-slate-900 text-sm"
                  >
                    <option value="real_world">Real World</option>
                    <option value="practical">Practical</option>
                    <option value="simulation">Simulation</option>
                  </select>
                </div>
              </div>
              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setModal({ mode: null })}
                  className="px-4 py-2 bg-white border border-slate-300 hover:border-slate-400 text-slate-700 rounded-lg transition-all text-sm"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg transition-all disabled:opacity-50 text-sm"
                >
                  {submitting ? "Creating..." : "Create Project"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {modal.mode === "edit" && modal.project && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white border border-slate-200 rounded-xl p-6 w-full max-w-lg shadow-2xl">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-slate-900">Edit Project</h3>
              <button
                type="button"
                onClick={() => setModal({ mode: null })}
                className="text-slate-400 hover:text-slate-600 text-xl leading-none"
              >
                &times;
              </button>
            </div>
            <form onSubmit={handleUpdateProject} className="space-y-4">
              <div>
                <label
                  htmlFor="edit-project-name"
                  className="block text-sm font-medium text-slate-700 mb-1"
                >
                  Name
                </label>
                <input
                  id="edit-project-name"
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-slate-900 focus:outline-none focus:border-slate-900 text-sm"
                />
              </div>
              <div>
                <label
                  htmlFor="edit-project-description"
                  className="block text-sm font-medium text-slate-700 mb-1"
                >
                  Description
                </label>
                <textarea
                  id="edit-project-description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-slate-900 focus:outline-none focus:border-slate-900 text-sm"
                  rows={3}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label
                    htmlFor="edit-project-status"
                    className="block text-sm font-medium text-slate-700 mb-1"
                  >
                    Status
                  </label>
                  <select
                    id="edit-project-status"
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                    className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-slate-900 focus:outline-none focus:border-slate-900 text-sm"
                  >
                    {statuses.map((s) => (
                      <option key={s} value={s}>
                        {s}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label
                    htmlFor="edit-project-type"
                    className="block text-sm font-medium text-slate-700 mb-1"
                  >
                    Type
                  </label>
                  <select
                    id="edit-project-type"
                    value={formData.project_type}
                    onChange={(e) => setFormData({ ...formData, project_type: e.target.value })}
                    className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-slate-900 focus:outline-none focus:border-slate-900 text-sm"
                  >
                    <option value="real_world">Real World</option>
                    <option value="practical">Practical</option>
                    <option value="simulation">Simulation</option>
                  </select>
                </div>
              </div>
              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setModal({ mode: null })}
                  className="px-4 py-2 bg-white border border-slate-300 hover:border-slate-400 text-slate-700 rounded-lg transition-all text-sm"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg transition-all disabled:opacity-50 text-sm"
                >
                  {submitting ? "Saving..." : "Save Changes"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {modal.mode === "delete" && modal.project && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white border border-slate-200 rounded-xl p-6 w-full max-w-md shadow-2xl">
            <h3 className="text-lg font-semibold text-slate-900 mb-2">Delete Project</h3>
            <p className="text-slate-500 text-sm mb-6">
              Are you sure you want to delete &quot;{modal.project.name}&quot;? This action cannot
              be undone.
            </p>
            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setModal({ mode: null })}
                className="px-4 py-2 bg-white border border-slate-300 hover:border-slate-400 text-slate-700 rounded-lg transition-all text-sm"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleDeleteProject}
                disabled={submitting}
                className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg transition-all disabled:opacity-50 text-sm"
              >
                {submitting ? "Deleting..." : "Delete"}
              </button>
            </div>
          </div>
        </div>
      )}

      {modal.mode === "requirements" && modal.project && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white border border-slate-200 rounded-xl p-6 w-full max-w-3xl shadow-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-slate-900">
                Requirements - {modal.project.name}
              </h3>
              <button
                type="button"
                onClick={() => setModal({ mode: null })}
                className="text-slate-400 hover:text-slate-600 text-xl leading-none"
              >
                &times;
              </button>
            </div>

            <form
              onSubmit={handleCreateRequirement}
              className="bg-slate-50 border border-slate-200 rounded-lg p-4 mb-6 space-y-4"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label
                    htmlFor="req-capability"
                    className="block text-sm font-medium text-slate-700 mb-1"
                  >
                    Capability
                  </label>
                  <select
                    id="req-capability"
                    required
                    value={reqForm.capability_id}
                    onChange={(e) => setReqForm({ ...reqForm, capability_id: e.target.value })}
                    className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-slate-900 focus:outline-none focus:border-slate-900 text-sm"
                  >
                    <option value="">Select capability</option>
                    {capabilities.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label
                    htmlFor="req-proficiency"
                    className="block text-sm font-medium text-slate-700 mb-1"
                  >
                    Min Proficiency (1-5)
                  </label>
                  <input
                    id="req-proficiency"
                    type="number"
                    min={1}
                    max={5}
                    required
                    value={reqForm.minimum_proficiency_level}
                    onChange={(e) =>
                      setReqForm({
                        ...reqForm,
                        minimum_proficiency_level: Number.parseInt(e.target.value),
                      })
                    }
                    className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-slate-900 focus:outline-none focus:border-slate-900 text-sm"
                  />
                </div>
                <div>
                  <label
                    htmlFor="req-importance"
                    className="block text-sm font-medium text-slate-700 mb-1"
                  >
                    Importance (0-1)
                  </label>
                  <input
                    id="req-importance"
                    type="number"
                    min={0}
                    max={1}
                    step={0.1}
                    required
                    value={reqForm.importance}
                    onChange={(e) =>
                      setReqForm({ ...reqForm, importance: Number.parseFloat(e.target.value) })
                    }
                    className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-slate-900 focus:outline-none focus:border-slate-900 text-sm"
                  />
                </div>
                <div className="flex items-center">
                  <label className="flex items-center gap-2 text-sm text-slate-700">
                    <input
                      type="checkbox"
                      checked={reqForm.required}
                      onChange={(e) => setReqForm({ ...reqForm, required: e.target.checked })}
                      className="rounded border-slate-300 bg-white text-slate-900 focus:ring-slate-900"
                    />
                    Required
                  </label>
                </div>
              </div>
              <div>
                <label
                  htmlFor="req-description"
                  className="block text-sm font-medium text-slate-700 mb-1"
                >
                  Description
                </label>
                <input
                  id="req-description"
                  type="text"
                  value={reqForm.description}
                  onChange={(e) => setReqForm({ ...reqForm, description: e.target.value })}
                  className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-slate-900 focus:outline-none focus:border-slate-900 text-sm"
                />
              </div>
              <button
                type="submit"
                disabled={submitting}
                className="w-full px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg transition-all disabled:opacity-50 text-sm"
              >
                {submitting ? "Adding..." : "Add Requirement"}
              </button>
            </form>

            <div className="space-y-2">
              {requirements.length === 0 ? (
                <p className="text-slate-500 text-center py-4 text-sm">No requirements yet.</p>
              ) : (
                requirements.map((req) => (
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
                        {req.importance} | {req.required ? "Required" : "Optional"}
                      </p>
                      {req.description && (
                        <p className="text-slate-400 text-xs mt-1">{req.description}</p>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => handleUpdateRequirement({ ...req, required: !req.required })}
                        className="text-xs px-2 py-1 bg-white border border-slate-300 hover:border-slate-400 text-slate-700 rounded-md transition-all"
                      >
                        Toggle Required
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDeleteRequirement(req.id)}
                        className="text-xs px-2 py-1 bg-white border border-red-300 hover:border-red-400 text-red-600 rounded-md transition-all"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {modal.mode === "matches" && modal.project && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white border border-slate-200 rounded-xl p-6 w-full max-w-5xl shadow-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-slate-900">
                Candidate Matches - {modal.project.name}
              </h3>
              <button
                type="button"
                onClick={() => {
                  setModal({ mode: null });
                  setMatches(null);
                }}
                className="text-slate-400 hover:text-slate-600 text-xl leading-none"
              >
                &times;
              </button>
            </div>

            {matchesLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="w-5 h-5 border-2 border-slate-900 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : matches ? (
              <>
                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                    <p className="text-slate-500 text-xs font-medium">Total Candidates</p>
                    <p className="text-xl font-semibold text-slate-900 mt-1">
                      {matches.total_candidates}
                    </p>
                  </div>
                  <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                    <p className="text-slate-500 text-xs font-medium">Eligible</p>
                    <p className="text-xl font-semibold text-emerald-600 mt-1">
                      {matches.eligible_count}
                    </p>
                  </div>
                  <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                    <p className="text-slate-500 text-xs font-medium">Match Quality</p>
                    <p className="text-xl font-semibold text-slate-900 mt-1">
                      {matches.matches.length > 0
                        ? `${Math.round(matches.matches.reduce((sum, m) => sum + m.match_score, 0) / matches.matches.length)}%`
                        : "N/A"}
                    </p>
                  </div>
                </div>

                {matches.matches.length === 0 ? (
                  <p className="text-slate-500 text-center py-8 text-sm">No candidates found.</p>
                ) : (
                  <div className="border border-slate-200 rounded-lg overflow-hidden">
                    <table className="w-full text-sm">
                      <thead className="bg-slate-50 border-b border-slate-200">
                        <tr>
                          <th className="text-left px-4 py-3 font-medium text-slate-500">
                            Candidate
                          </th>
                          <th className="text-left px-4 py-3 font-medium text-slate-500">Match</th>
                          <th className="text-left px-4 py-3 font-medium text-slate-500">
                            Coverage
                          </th>
                          <th className="text-left px-4 py-3 font-medium text-slate-500">
                            Strengths
                          </th>
                          <th className="text-left px-4 py-3 font-medium text-slate-500">Gaps</th>
                          <th className="text-left px-4 py-3 font-medium text-slate-500">
                            Missing
                          </th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-200">
                        {matches.matches.map((m) => (
                          <tr key={m.user_id} className="hover:bg-slate-50">
                            <td className="px-4 py-3">
                              <div className="font-medium text-slate-900">{m.user_name}</div>
                              <div className="text-slate-500 text-xs">{m.user_email}</div>
                            </td>
                            <td className="px-4 py-3">
                              <div className="flex items-center gap-2">
                                <span
                                  className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                                    m.eligible
                                      ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                                      : "bg-red-50 text-red-700 border border-red-200"
                                  }`}
                                >
                                  {m.eligible ? "Eligible" : "Not Eligible"}
                                </span>
                                <span className="font-mono text-slate-900 font-medium">
                                  {m.match_score}%
                                </span>
                              </div>
                            </td>
                            <td className="px-4 py-3 text-slate-600">
                              {Math.round(m.coverage_ratio * 100)}%
                            </td>
                            <td className="px-4 py-3">
                              <div className="flex flex-wrap gap-1">
                                {m.matched.slice(0, 2).map((match) => (
                                  <span
                                    key={match.requirement_id}
                                    className="inline-flex items-center px-2 py-0.5 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded text-xs"
                                  >
                                    {match.capability_name || match.capability_id}
                                  </span>
                                ))}
                                {m.matched.length > 2 && (
                                  <span className="text-xs text-slate-500">
                                    +{m.matched.length - 2}
                                  </span>
                                )}
                              </div>
                            </td>
                            <td className="px-4 py-3">
                              <div className="flex flex-wrap gap-1">
                                {m.gaps.slice(0, 2).map((gap) => (
                                  <span
                                    key={gap.requirement_id}
                                    className="inline-flex items-center px-2 py-0.5 bg-amber-50 text-amber-700 border border-amber-200 rounded text-xs"
                                  >
                                    {gap.capability_name || gap.capability_id}
                                  </span>
                                ))}
                                {m.gaps.length > 2 && (
                                  <span className="text-xs text-slate-500">
                                    +{m.gaps.length - 2}
                                  </span>
                                )}
                              </div>
                            </td>
                            <td className="px-4 py-3">
                              <div className="flex flex-wrap gap-1">
                                {m.missing.slice(0, 2).map((missing) => (
                                  <span
                                    key={missing.requirement_id}
                                    className="inline-flex items-center px-2 py-0.5 bg-red-50 text-red-700 border border-red-200 rounded text-xs"
                                  >
                                    {missing.capability_name || missing.capability_id}
                                  </span>
                                ))}
                                {m.missing.length > 2 && (
                                  <span className="text-xs text-slate-500">
                                    +{m.missing.length - 2}
                                  </span>
                                )}
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                {matches.total_pages > 1 && (
                  <div className="flex items-center justify-between mt-4 pt-4 border-t border-slate-200">
                    <p className="text-sm text-slate-500">
                      Page {matches.page} of {matches.total_pages}
                    </p>
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        disabled={matches.page <= 1}
                        onClick={() => {
                          const projectId = modal.project?.id;
                          if (projectId) loadMatches(projectId);
                        }}
                        className="px-3 py-1.5 bg-white border border-slate-300 hover:border-slate-400 text-slate-700 text-sm font-medium rounded-md transition-all disabled:opacity-50"
                      >
                        Previous
                      </button>
                      <button
                        type="button"
                        disabled={matches.page >= matches.total_pages}
                        onClick={() => {
                          const projectId = modal.project?.id;
                          if (projectId) loadMatches(projectId);
                        }}
                        className="px-3 py-1.5 bg-white border border-slate-300 hover:border-slate-400 text-slate-700 text-sm font-medium rounded-md transition-all disabled:opacity-50"
                      >
                        Next
                      </button>
                    </div>
                  </div>
                )}
              </>
            ) : null}
          </div>
        </div>
      )}
    </main>
  );
}
