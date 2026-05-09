import Link from "next/link"
import { Box, Typography, Divider } from "@mui/material"
import { getEvaluations } from "@/lib/api"
import { Verdict } from "@/types"
import { EvaluationSummary } from "@/lib/api"


const VERDICT_COLOR: Record<Verdict, string> = {
  ADEQUATE:   "#22c55e",
  REVIEW:     "#eab308",
  INADEQUATE: "#ef4444",
  UNKNOWN:    "#888888",
}

export default async function HistoryPage() {
  let evaluations: EvaluationSummary[] = []
  try {
    evaluations = await getEvaluations()
  } catch {
    evaluations = []
  }

  return (
    <Box sx={{ minHeight: "100vh", px: { xs: 3, md: 6 }, py: 5, maxWidth: 900, mx: "auto" }}>
      <Typography variant="overline" sx={{ color: "#555", display: "block", mb: 0.5 }}>
        past evaluations
      </Typography>
      <Typography variant="h4" sx={{ fontWeight: 700, fontSize: { xs: "1.5rem", sm: "2rem" }, mb: 4 }}>
        history
      </Typography>

      <Divider sx={{ borderColor: "#1e1e1e", mb: 4 }} />

      {evaluations.length === 0 ? (
        <Typography sx={{ color: "#444", fontFamily: '"JetBrains Mono", monospace', fontSize: "0.85rem" }}>
          no evaluations yet — run one from the evaluate page.
        </Typography>
      ) : (
        <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5 }}>
          {evaluations.map((ev) => {
            const color = VERDICT_COLOR[ev.verdict as Verdict] ?? "#888"
            const location = [ev.city, ev.state, ev.country].filter(Boolean).join(", ")
            const date = new Date(ev.created_at).toLocaleDateString("en-US", {
              month: "short", day: "numeric", year: "numeric",
            })

            return (
              <Link key={ev.id} href={`/results/${ev.id}`} style={{ textDecoration: "none" }}>
                <Box sx={{
                  display:        "flex",
                  alignItems:     "center",
                  justifyContent: "space-between",
                  border:         "1px solid #1a1a1a",
                  borderLeft:     `3px solid ${color}`,
                  p:              2,
                  borderRadius:   "2px",
                  background:     "#0d0d0d",
                  transition:     "background 0.15s, border-color 0.15s",
                  "&:hover":      { background: "#141414", borderColor: "#333" },
                  gap:            2,
                }}>

                  <Box sx={{ flex: 1, minWidth: 0 }}>
                    <Typography sx={{
                      fontFamily: '"JetBrains Mono", monospace',
                      fontSize:   "0.85rem",
                      color:      "#e8e8e8",
                      mb:         0.25,
                      overflow:   "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}>
                      {location || "unknown location"}
                    </Typography>
                    <Typography sx={{
                      fontFamily: '"JetBrains Mono", monospace',
                      fontSize:   "0.7rem",
                      color:      "#444",
                    }}>
                      {ev.snapped_lat.toFixed(5)}, {ev.snapped_lng.toFixed(5)}
                    </Typography>
                  </Box>

                  <Typography sx={{
                    fontFamily: '"JetBrains Mono", monospace',
                    fontSize:   "0.72rem",
                    color:      "#444",
                    flexShrink: 0,
                  }}>
                    {date}
                  </Typography>

                  <Box sx={{ textAlign: "right", flexShrink: 0 }}>
                    <Typography sx={{
                      fontFamily: '"JetBrains Mono", monospace',
                      fontSize:   "1.2rem",
                      fontWeight: 700,
                      color,
                      lineHeight: 1,
                    }}>
                      {ev.score !== null ? ev.score.toFixed(1) : "—"}
                    </Typography>
                    <Typography sx={{
                      fontFamily:    '"JetBrains Mono", monospace',
                      fontSize:      "0.65rem",
                      color,
                      textTransform: "uppercase",
                      letterSpacing: "0.08em",
                    }}>
                      {ev.verdict.toLowerCase()}
                    </Typography>
                  </Box>
                </Box>
              </Link>
            )
          })}
        </Box>
      )}
    </Box>
  )
}
