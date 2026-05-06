"use client"

import { Box, Typography } from "@mui/material"
import { Verdict } from "@/types"

const VERDICT_COLOR: Record<Verdict, string> = {
  ADEQUATE:   "#22c55e",
  REVIEW:     "#eab308",
  INADEQUATE: "#ef4444",
  UNKNOWN:    "#888888",
}

const VERDICT_LABEL: Record<Verdict, string> = {
  ADEQUATE:   "adequate",
  REVIEW:     "needs review",
  INADEQUATE: "inadequate",
  UNKNOWN:    "unknown",
}

export default function ScoreDisplay({ score, verdict }: { score: number | null; verdict: Verdict }) {
  const color = VERDICT_COLOR[verdict]
  return (
    <Box sx={{
      display: "flex", flexDirection: "column", alignItems: "flex-start",
      border: `1px solid ${color}22`, borderLeft: `3px solid ${color}`,
      p: 3, background: `${color}08`, borderRadius: "2px", minWidth: 180,
    }}>
      <Typography variant="overline" sx={{ color: "#555", lineHeight: 1, mb: 1 }}>
        safety score
      </Typography>
      <Typography sx={{
        fontFamily: '"JetBrains Mono", monospace',
        fontSize: "4rem", fontWeight: 700, lineHeight: 1, color,
      }}>
        {score !== null ? score.toFixed(1) : "—"}
      </Typography>
      <Typography sx={{
        fontFamily: '"JetBrains Mono", monospace', fontSize: "0.8rem",
        color, mt: 0.5, textTransform: "uppercase", letterSpacing: "0.1em",
      }}>
        {VERDICT_LABEL[verdict]}
      </Typography>
    </Box>
  )
}
