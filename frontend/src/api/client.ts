export const API_BASE = "http://localhost:8000";

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`API ${res.status}: ${path}`);
  return res.json();
}

export function mediaUrl(mediaId: number): string {
  return `${API_BASE}/api/media/${mediaId}`;
}

import type {
  PresentationSummary,
  PresentationDetail,
  SlideData,
} from "./types";

export const api = {
  listPresentations: () => fetchJson<PresentationSummary[]>("/api/presentations"),
  getPresentation: (dbNo: number) => fetchJson<PresentationDetail>(`/api/presentations/${dbNo}`),
  getSlide: (id: number) => fetchJson<SlideData>(`/api/slides/${id}`),
};
