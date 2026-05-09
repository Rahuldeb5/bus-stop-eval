export type Verdict = "ADEQUATE" | "REVIEW" | "INADEQUATE" | "UNKNOWN"

export interface CriterionResult {
  criterion:  string
  passed:     boolean | null
  importance: "critical" | "high" | "medium" | "low" | null
  notes:      string | null
}

export interface FailureItem {
  criterion: string
  notes:     string | null
}

export interface Failures {
  critical: FailureItem[]
  high:     FailureItem[]
  medium:   FailureItem[]
  low:      FailureItem[]
}
export interface EvaluationResult {
  job_id:      string
  city:        string | null
  state:       string | null
  country:     string | null
  snapped_lat: number
  snapped_lng: number
  score:       number | null
  verdict:     Verdict
  failures:    Failures
  results:     CriterionResult[]
  image_urls:  string[]
}
