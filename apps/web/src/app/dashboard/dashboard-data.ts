export function getDashboardRecords<T>(value: unknown): T[] {
  return Array.isArray(value) ? (value as T[]) : [];
}

export function getSafeText(value: unknown): string | null {
  if (typeof value !== "string") return null;
  const text = value.trim();
  return text.length > 0 ? text : null;
}

function getFiniteNumber(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

/** Backend ProficiencyPolicy v1 maps emerging/developing/proficient/advanced to levels 1–4. */
export function getSafeProficiency(value: unknown): number | null {
  const level = getFiniteNumber(value);
  return level !== null && Number.isInteger(level) && level >= 1 && level <= 4 ? level : null;
}

/** CapabilityScoringService normalizes capability scores to 0–100. This is a score, not completion progress. */
export function getSafeCapabilityScore(value: unknown): number | null {
  const score = getFiniteNumber(value);
  return score !== null && score >= 0 && score <= 100 ? score : null;
}

/** AssessmentAttemptService calculates percentage as earned score / maximum score × 100. */
export function getSafePercentage(value: unknown): number | null {
  const percentage = getFiniteNumber(value);
  return percentage !== null && percentage >= 0 && percentage <= 100 ? percentage : null;
}

export function getSafeAssessmentStatus(value: unknown): string {
  switch (value) {
    case "in_progress":
      return "In progress";
    case "submitted":
      return "Submitted";
    default:
      return "Status unavailable";
  }
}

export function formatDashboardDate(value: unknown): string | null {
  if (typeof value !== "string" || value.trim() === "") return null;
  const timestamp = Date.parse(value);
  if (!Number.isFinite(timestamp)) return null;
  return new Date(timestamp).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}
