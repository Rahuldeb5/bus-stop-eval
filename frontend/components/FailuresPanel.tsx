"use client"

import { Box, Typography, Stack } from "@mui/material"
import { Failures, CriterionResult } from "@/types"

const TIER_CONFIG = {
  critical: { color: "#ef4444", label: "critical",  border: "#ef444422" },
  high:     { color: "#f97316", label: "high",       border: "#f9731622" },
  medium:   { color: "#eab308", label: "medium",     border: "#eab30822" },
  low:      { color: "#6b7280", label: "low",        border: "#6b728022" },
} as const

const CRITERION_LABELS: Record<string, string> = {
  railroad: "railroad proximity", slope: "road slope", freeway_ramp: "freeway ramp",
  traffic_signal: "traffic signal", divided_highway: "divided highway",
  right_turn_lane: "right turn lane", uturn: "u-turn / dead end", bike_lane: "bike lane",
  sidewalk: "sidewalk access", waiting_area: "waiting area", visibility: "sight lines",
  ada: "ADA accessibility", obstructions: "obstructions", water_body: "water body",
}

function FailureTier({ tier, items }: { tier: keyof typeof TIER_CONFIG; items: { criterion: string; notes: string | null }[] }) {
  if (!items.length) return null
  const { color, label, border } = TIER_CONFIG[tier]
  return (
    <Box>
      <Typography variant="overline" sx={{ color: "#444", display: "block", mb: 1 }}>
        {label} failures
      </Typography>
      <Stack spacing={1}>
        {items.map(item => (
          <Box key={item.criterion} sx={{
            border: `1px solid ${border}`, borderLeft: `3px solid ${color}`,
            p: 1.5, borderRadius: "2px", background: `${color}05`,
          }}>
            <Typography sx={{
              fontFamily: '"JetBrains Mono", monospace',
              fontSize: "0.8rem", color, mb: item.notes ? 0.5 : 0,
            }}>
              {CRITERION_LABELS[item.criterion] ?? item.criterion}
            </Typography>
            {item.notes && (
              <Typography sx={{ fontSize: "0.8rem", color: "#666", lineHeight: 1.5 }}>
                {item.notes.replace(/;$/, "")}
              </Typography>
            )}
          </Box>
        ))}
      </Stack>
    </Box>
  )
}

export default function FailuresPanel({ failures, results }: { failures: Failures; results: CriterionResult[] }) {
  const passing = results.filter(r => r.passed === true)
  const skipped = results.filter(r => r.passed === null)
  const totalFailures = Object.values(failures).flat().length

  return (
    <Box>
      <Typography variant="overline" sx={{ color: "#555", display: "block", mb: 2 }}>findings</Typography>

      {totalFailures === 0 ? (
        <Typography sx={{ color: "#22c55e", fontFamily: '"JetBrains Mono", monospace', fontSize: "0.85rem" }}>
          no failures detected
        </Typography>
      ) : (
        <Stack spacing={3}>
          <FailureTier tier="critical" items={failures.critical} />
          <FailureTier tier="high"     items={failures.high} />
          <FailureTier tier="medium"   items={failures.medium} />
          <FailureTier tier="low"      items={failures.low} />
        </Stack>
      )}

      {passing.length > 0 && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="overline" sx={{ color: "#444", display: "block", mb: 1.5 }}>
            passing ({passing.length})
          </Typography>
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
            {passing.map(r => (
              <Typography key={r.criterion} sx={{
                fontFamily: '"JetBrains Mono", monospace', fontSize: "0.72rem",
                color: "#22c55e", border: "1px solid #22c55e22",
                px: 1, py: 0.25, borderRadius: "2px", background: "#22c55e08",
              }}>
                ✓ {CRITERION_LABELS[r.criterion] ?? r.criterion}
              </Typography>
            ))}
          </Box>
        </Box>
      )}

      {skipped.length > 0 && (
        <Box sx={{ mt: 3 }}>
          <Typography variant="overline" sx={{ color: "#333", display: "block", mb: 1 }}>
            inconclusive — human review required ({skipped.length})
          </Typography>
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
            {skipped.map(r => (
              <Typography key={r.criterion} sx={{
                fontFamily: '"JetBrains Mono", monospace', fontSize: "0.72rem",
                color: "#555", border: "1px solid #333", px: 1, py: 0.25, borderRadius: "2px",
              }}>
                ? {CRITERION_LABELS[r.criterion] ?? r.criterion}
              </Typography>
            ))}
          </Box>
        </Box>
      )}
    </Box>
  )
}
