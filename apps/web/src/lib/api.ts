const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

let refreshToken: string | null = null;
let onUnauthorized: (() => void) | null = null;

export function setAuthCallbacks(
  refreshTokenValue: string | null,
  unauthorizedHandler: (() => void) | null,
) {
  refreshToken = refreshTokenValue;
  onUnauthorized = unauthorizedHandler;
}

export interface UserProfile {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_verified: boolean;
  is_superuser: boolean;
  role: string;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: UserProfile;
}

export interface RegistrationResponse {
  message: string;
  email: string;
  username: string;
  is_verified: boolean;
}

export interface Capability {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  category: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserCapability {
  id: string;
  user_id: string;
  capability_id: string;
  proficiency_level: number;
  score: number;
  confidence: number;
  verified: boolean;
  last_assessed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface Assessment {
  id: string;
  capability_id: string;
  title: string;
  slug: string;
  description: string | null;
  difficulty: string;
  time_limit_minutes: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AssessmentQuestion {
  id: string;
  assessment_id: string;
  question_order: number;
  question_type: string;
  question_text: string;
  options_json: string | null;
  points: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AssessmentAttempt {
  id: string;
  user_id: string;
  assessment_id: string;
  status: string;
  question_count: number;
  answered_count: number;
  correct_count: number;
  score: number | null;
  max_score: number | null;
  percentage: number | null;
  started_at: string;
  submitted_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface AssessmentAnswer {
  id: string;
  attempt_id: string;
  question_id: string;
  selected_answer: string;
  is_correct: boolean;
  points_earned: number;
  answered_at: string;
  created_at: string;
  updated_at: string;
}

export interface AssessmentAttemptResult {
  attempt: AssessmentAttempt;
  answers: AssessmentAnswer[];
  capability: {
    user_id: string;
    capability_id: string;
    proficiency_level: number;
    score: number;
    confidence: number;
    verified: boolean;
    last_assessed_at: string | null;
  } | null;
}

export interface CapabilityScoreHistory {
  id: string;
  user_id: string;
  capability_id: string;
  attempt_id: string | null;
  evidence_id: string | null;
  score: number;
  proficiency: string | null;
  confidence: number;
  previous_score: number | null;
  score_delta: number | null;
  source: string;
  reason: string | null;
  metadata_json: string | null;
  created_at: string;
}

export interface Project {
  id: string;
  name: string;
  description: string | null;
  status: string;
  project_type: string;
  owner_id: string;
  organization_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProjectRequirement {
  id: string;
  project_id: string;
  capability_id: string;
  capability_name: string | null;
  description: string | null;
  minimum_proficiency_level: number;
  importance: number;
  required: boolean;
  created_at: string;
  updated_at: string;
}

export interface RequirementMatch {
  requirement_id: string;
  capability_id: string;
  capability_name: string | null;
  required_level: number;
  current_level: number | null;
  importance: number;
  required: boolean;
  status: string;
  gap: number;
}

export interface ProjectMatchResult {
  project_id: string;
  user_id: string;
  eligible: boolean;
  match_score: number;
  coverage_ratio: number;
  matched: RequirementMatch[];
  gaps: RequirementMatch[];
  missing: RequirementMatch[];
}

export interface LearnerProfile {
  id: string;
  user_id: string;
  display_name: string | null;
  headline: string | null;
  bio: string | null;
  location: string | null;
  profile_image_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface EngineeringPassport {
  profile: {
    id: string;
    email: string;
    username: string;
    first_name: string;
    last_name: string;
    is_verified: boolean;
    display_name: string | null;
    headline: string | null;
    bio: string | null;
    location: string | null;
  };
  capabilities: Array<{
    id: string;
    name: string;
    slug: string;
    category: string;
    proficiency_level: number;
    score: number;
    confidence: number;
    verified: boolean;
    last_assessed_at: string | null;
  }>;
  assessment_history: Array<{
    attempt_id: string;
    assessment_id: string;
    assessment_title: string;
    status: string;
    score: number | null;
    max_score: number | null;
    percentage: number | null;
    submitted_at: string | null;
  }>;
  capability_history: Array<{
    id: string;
    score: number;
    proficiency: string | null;
    confidence: number;
    previous_score: number | null;
    score_delta: number | null;
    source: string;
    reason: string | null;
    created_at: string;
  }>;
  project_experience: Array<{
    id: string;
    name: string;
    description: string | null;
    status: string;
    project_type: string;
    created_at: string;
  }>;
  generated_at: string;
}

export async function apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const maxRetries = 2;
  const retryableStatuses = new Set([500, 502, 503, 504]);

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    const data = await response.json().catch(() => ({}));

    if (response.ok) {
      return data as T;
    }

    const shouldRetry = retryableStatuses.has(response.status) && attempt < maxRetries;

    if (shouldRetry) {
      await new Promise((resolve) => setTimeout(resolve, 500 * (attempt + 1)));
      continue;
    }

    if (response.status === 401 && token && refreshToken) {
      try {
        const refreshed = await refreshAccessToken(refreshToken);
        if (typeof window !== "undefined") {
          localStorage.setItem("access_token", refreshed.access_token);
          localStorage.setItem("refresh_token", refreshed.refresh_token);
        }
        const retryHeaders: Record<string, string> = {
          "Content-Type": "application/json",
          ...(options.headers as Record<string, string>),
          Authorization: `Bearer ${refreshed.access_token}`,
        };
        const retryResponse = await fetch(`${API_BASE_URL}${endpoint}`, {
          ...options,
          headers: retryHeaders,
        });
        const retryData = await retryResponse.json().catch(() => ({}));
        if (retryResponse.ok) {
          return retryData as T;
        }
      } catch {
        if (onUnauthorized) {
          onUnauthorized();
        }
      }
    }

    const message =
      data.error?.message || data.detail || `Request failed with status ${response.status}`;
    throw new Error(message);
  }

  throw new Error("Request failed after retries.");
}

export async function refreshAccessToken(refreshToken: string): Promise<AuthResponse> {
  return apiRequest<AuthResponse>("/auth/refresh", {
    method: "POST",
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
}

export async function fetchHealth() {
  return apiRequest<{ success: boolean; status: string; service: string }>("/health");
}

export async function fetchCapabilities() {
  return apiRequest<Capability[]>("/capabilities");
}

export async function fetchCapabilityById(id: string) {
  return apiRequest<Capability>(`/capabilities/${id}`);
}

export async function fetchUserCapabilities(userId: string) {
  return apiRequest<UserCapability[]>(`/user-capabilities/${userId}/capabilities`);
}

export async function fetchAssessments() {
  return apiRequest<Assessment[]>("/assessments");
}

export async function fetchAssessmentById(id: string) {
  return apiRequest<Assessment>(`/assessments/${id}`);
}

export async function fetchAssessmentQuestions(assessmentId: string) {
  return apiRequest<AssessmentQuestion[]>(`/assessment-questions/assessment/${assessmentId}`);
}

export async function createAssessmentAttempt(assessmentId: string) {
  return apiRequest<AssessmentAttempt>("/assessment-attempts", {
    method: "POST",
    body: JSON.stringify({ assessment_id: assessmentId }),
  });
}

export async function fetchMyAssessmentAttempts() {
  return apiRequest<AssessmentAttempt[]>("/assessment-attempts/mine");
}

export async function submitAnswer(attemptId: string, questionId: string, selectedAnswer: string) {
  return apiRequest<AssessmentAnswer>("/assessment-answers", {
    method: "POST",
    body: JSON.stringify({
      attempt_id: attemptId,
      question_id: questionId,
      selected_answer: selectedAnswer,
    }),
  });
}

export async function submitAssessmentAttempt(attemptId: string) {
  return apiRequest<AssessmentAttemptResult>(`/assessment-attempts/${attemptId}/submit`, {
    method: "POST",
  });
}

export async function fetchAttemptResult(attemptId: string) {
  return apiRequest<AssessmentAttemptResult>(`/assessment-attempts/${attemptId}/result`);
}

export async function fetchAttemptAnswers(attemptId: string) {
  return apiRequest<AssessmentAnswer[]>(`/assessment-answers/attempt/${attemptId}`);
}

export async function fetchCapabilityHistory(userId: string, capabilityId: string) {
  return apiRequest<CapabilityScoreHistory[]>(
    `/capability-history/user/${userId}/capability/${capabilityId}`,
  );
}

export async function fetchProjects() {
  return apiRequest<Project[]>("/projects");
}

export async function fetchProjectById(id: string) {
  return apiRequest<Project>(`/projects/${id}`);
}

export async function fetchProjectMatch(projectId: string) {
  return apiRequest<ProjectMatchResult>(`/projects/${projectId}/match`);
}

export async function fetchOwnerProjects(ownerId: string) {
  return apiRequest<Project[]>(`/projects/owner/${ownerId}`);
}

export async function createProject(payload: {
  name: string;
  description?: string;
  project_type?: string;
  owner_id: string;
  organization_id?: string;
}) {
  return apiRequest<Project>("/projects", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateProject(
  projectId: string,
  payload: { name?: string; description?: string; status?: string; project_type?: string },
) {
  return apiRequest<Project>(`/projects/${projectId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function deleteProject(projectId: string) {
  return apiRequest<{ success: boolean; project_id: string }>(`/projects/${projectId}`, {
    method: "DELETE",
  });
}

export async function fetchProjectRequirements(projectId: string) {
  return apiRequest<ProjectRequirement[]>(`/projects/${projectId}/requirements`);
}

export async function createProjectRequirement(
  projectId: string,
  payload: {
    project_id: string;
    capability_id: string;
    description?: string;
    minimum_proficiency_level?: number;
    importance?: number;
    required?: boolean;
  },
) {
  return apiRequest<ProjectRequirement>(`/projects/${projectId}/requirements`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateProjectRequirement(
  requirementId: string,
  payload: {
    description?: string;
    minimum_proficiency_level?: number;
    importance?: number;
    required?: boolean;
  },
) {
  return apiRequest<ProjectRequirement>(`/projects/requirements/${requirementId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function deleteProjectRequirement(requirementId: string) {
  return apiRequest<{ success: boolean; requirement_id: string }>(
    `/projects/requirements/${requirementId}`,
    {
      method: "DELETE",
    },
  );
}

export interface ProjectMatchesResponse {
  project_id: string;
  total_candidates: number;
  eligible_count: number;
  page: number;
  page_size: number;
  total_pages: number;
  matches: Array<{
    user_id: string;
    user_email: string;
    user_name: string;
    eligible: boolean;
    match_score: number;
    coverage_ratio: number;
    matched: RequirementMatch[];
    gaps: RequirementMatch[];
    missing: RequirementMatch[];
  }>;
}

export async function fetchProjectMatches(projectId: string, page = 1, pageSize = 20) {
  const params = new URLSearchParams();
  params.set("page", String(page));
  params.set("page_size", String(pageSize));
  return apiRequest<ProjectMatchesResponse>(`/projects/${projectId}/matches?${params.toString()}`);
}

export async function fetchLearnerProfile() {
  return apiRequest<LearnerProfile>("/learner/profile");
}

export async function createLearnerProfile(payload: {
  display_name?: string;
  headline?: string;
  bio?: string;
  location?: string;
  profile_image_url?: string;
}) {
  return apiRequest<LearnerProfile>("/learner/profile", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateLearnerProfile(payload: {
  display_name?: string;
  headline?: string;
  bio?: string;
  location?: string;
  profile_image_url?: string;
}) {
  return apiRequest<LearnerProfile>("/learner/profile", {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function fetchPassport() {
  return apiRequest<EngineeringPassport>("/learner/passport");
}

export async function verifyEmail(email: string, otp: string) {
  return apiRequest<AuthResponse>("/auth/verify-email", {
    method: "POST",
    body: JSON.stringify({ email, otp }),
  });
}

export async function resendVerification(email: string) {
  return apiRequest<{ message: string; email: string }>("/auth/resend-verification", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}

export async function forgotPassword(email: string) {
  return apiRequest<{ message: string }>("/auth/forgot-password", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}

export async function resetPassword(token: string, password: string, confirmPassword: string) {
  return apiRequest<{ message: string }>("/auth/reset-password", {
    method: "POST",
    body: JSON.stringify({ token, password, confirm_password: confirmPassword }),
  });
}
