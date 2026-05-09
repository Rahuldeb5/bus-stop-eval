import { EvaluationResult, Verdict } from "@/types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export interface EvaluationSummary {
  id:          string
  city:        string | null
  state:       string | null
  country:     string | null
  snapped_lat: number
  snapped_lng: number
  score:       number | null
  verdict:     Verdict
  created_at:  string
}

export async function evaluate(lat: number, lng: number): Promise<EvaluationResult> {
  const res = await fetch(`${API_BASE}/evaluate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ lat, lng }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail ?? `Request failed: ${res.status}`)
  }
  return res.json()
}

export async function getEvaluation(jobId: string): Promise<EvaluationResult> {
  const res = await fetch(`${API_BASE}/evaluation/${jobId}`)
  if (!res.ok) throw new Error("Evaluation not found")
  return res.json()
}

export function imageUrl(path: string): string {
  return `${API_BASE}${path}`
}

export async function getEvaluations(limit = 50): Promise<EvaluationSummary[]> {
  const res = await fetch(`${API_BASE}/evaluations?limit=${limit}`)
  if (!res.ok) throw new Error("Failed to fetch history")
  return res.json()
}
