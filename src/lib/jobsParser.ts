/* eslint-disable @typescript-eslint/no-explicit-any */
import { JobPosting } from "@/lib/types";

export function extractJobsFromText(text: string): any[] {
  if (!text) return [];

  const re = /<JOBS>\s*(?:```(?:json)?\s*)?(\[[\s\S]*?\])\s*(?:```)?\s*<\/JOBS>/i;
  const m = text.match(re);
  if (!m?.[1]) return [];

  try {
    return JSON.parse(m[1]);
  } catch {
    return [];
  }
}

export function normalizeJobs(items: any[]): JobPosting[] {
  const out: JobPosting[] = [];

  for (const it of items || []) {
    if (!it || typeof it !== "object") continue;

    const company = String(it.company ?? "").trim();
    const title = String(it.title ?? "").trim();
    const location = String(it.location ?? "").trim();
    const url = String(it.link ?? it.url ?? "").trim();
    const goodMatch = String(it["Good Match"] ?? it.goodMatch ?? "").trim();

    if (!url) continue;

    out.push({
      company: company || "—",
      title: title || "—",
      location: location || "—",
      url,
      goodMatch: goodMatch || "",
    });
  }

  return out.slice(0, 5);
}
