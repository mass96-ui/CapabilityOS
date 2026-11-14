import { describe, expect, it } from "vitest";
import {
  formatDashboardDate,
  getDashboardRecords,
  getSafeAssessmentStatus,
  getSafeCapabilityScore,
  getSafePercentage,
  getSafeProficiency,
  getSafeText,
} from "./dashboard-data";

describe("dashboard data helpers", () => {
  it("returns empty records for null, missing, or malformed collections", () => {
    expect(getDashboardRecords(undefined)).toEqual([]);
    expect(getDashboardRecords(null)).toEqual([]);
    expect(getDashboardRecords({})).toEqual([]);
    expect(getDashboardRecords([])).toEqual([]);
    expect(getDashboardRecords([1, 2])).toEqual([1, 2]);
  });

  it("accepts only non-empty text", () => {
    expect(getSafeText(" learner ")).toBe("learner");
    expect(getSafeText(" ")).toBeNull();
    expect(getSafeText(null)).toBeNull();
    expect(getSafeText(2)).toBeNull();
  });

  it("accepts only integer proficiency levels defined by the backend policy", () => {
    expect(getSafeProficiency(1)).toBe(1);
    expect(getSafeProficiency(4)).toBe(4);
    for (const value of [0, 5, -1, 2.5, Number.NaN, Number.POSITIVE_INFINITY, null, "3"]) {
      expect(getSafeProficiency(value)).toBeNull();
    }
  });

  it("validates normalized capability score boundaries without treating them as percentages", () => {
    expect(getSafeCapabilityScore(0)).toBe(0);
    expect(getSafeCapabilityScore(100)).toBe(100);
    expect(getSafeCapabilityScore(67.25)).toBe(67.25);
    for (const value of [-0.01, 100.01, Number.NaN, Number.NEGATIVE_INFINITY, null, "80"]) {
      expect(getSafeCapabilityScore(value)).toBeNull();
    }
  });

  it("validates assessment percentage boundaries and malformed optional values", () => {
    expect(getSafePercentage(0)).toBe(0);
    expect(getSafePercentage(100)).toBe(100);
    expect(getSafePercentage(73.5)).toBe(73.5);
    for (const value of [-1, 101, Number.NaN, Number.POSITIVE_INFINITY, null, undefined, "73.5"]) {
      expect(getSafePercentage(value)).toBeNull();
    }
  });

  it("maps only recognized backend assessment statuses", () => {
    expect(getSafeAssessmentStatus("in_progress")).toBe("In progress");
    expect(getSafeAssessmentStatus("submitted")).toBe("Submitted");
    for (const value of ["failed", "draft", "IN_PROGRESS", "", null, undefined, 1]) {
      expect(getSafeAssessmentStatus(value)).toBe("Status unavailable");
    }
  });

  it("formats valid dates and rejects missing or malformed dates", () => {
    expect(formatDashboardDate("2025-01-02T00:00:00Z")).toBeTruthy();
    expect(formatDashboardDate("2025-01-02")).toBeTruthy();
    expect(formatDashboardDate(null)).toBeNull();
    expect(formatDashboardDate(undefined)).toBeNull();
    expect(formatDashboardDate(" ")).toBeNull();
    expect(formatDashboardDate("not-a-date")).toBeNull();
    expect(formatDashboardDate(123)).toBeNull();
  });
});
