"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import {
  Box, Typography, TextField, Button, Alert,
  CircularProgress, Stack, Divider,
} from "@mui/material"
import { evaluate } from "@/lib/api"

const PHASES = [
  "fetching street view imagery...",
  "querying overpass api...",
  "running api checks...",
  "running visual checks...",
  "computing score...",
]

export default function HomePage() {
  const router = useRouter()
  const [lat, setLat]         = useState("")
  const [lng, setLng]         = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState<string | null>(null)
  const [phase, setPhase]     = useState("")

  async function handleSubmit() {
    const latN = parseFloat(lat)
    const lngN = parseFloat(lng)
    if (isNaN(latN) || isNaN(lngN)) { setError("Enter valid decimal coordinates."); return }
    if (latN < -90 || latN > 90 || lngN < -180 || lngN > 180) { setError("Coordinates out of range."); return }

    setError(null)
    setLoading(true)
    let i = 0
    setPhase(PHASES[0])
    const interval = setInterval(() => { i = (i + 1) % PHASES.length; setPhase(PHASES[i]) }, 5000)

    try {
      const result = await evaluate(latN, lngN)
      clearInterval(interval)
      router.push(`/results/${result.job_id}`)
    } catch (e: unknown) {
      clearInterval(interval)
      setError(e instanceof Error ? e.message : "Evaluation failed.")
      setLoading(false)
    }
  }

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        px: 3,
        position: "relative",
        overflow: "hidden",
        "&::before": {
          content: '""',
          position: "absolute",
          inset: 0,
          background: `
            radial-gradient(ellipse 80% 50% at 20% 60%, rgba(255,255,255,0.02) 0%, transparent 60%),
            repeating-linear-gradient(0deg, transparent, transparent 39px, rgba(255,255,255,0.02) 39px, rgba(255,255,255,0.02) 40px),
            repeating-linear-gradient(90deg, transparent, transparent 39px, rgba(255,255,255,0.02) 39px, rgba(255,255,255,0.02) 40px)
          `,
          pointerEvents: "none",
        },
      }}
    >
      <Box sx={{ width: "100%", maxWidth: 520, position: "relative", zIndex: 1 }}>
        <Typography variant="overline" sx={{ color: "#555", display: "block", mb: 1 }}>
          school bus stop safety
        </Typography>
        <Typography variant="h2" sx={{ fontSize: { xs: "2rem", sm: "2.8rem" }, fontWeight: 700, mb: 1, lineHeight: 1.1 }}>
          stop evaluator
        </Typography>
        <Typography sx={{ color: "#666", mb: 5, fontSize: "0.9rem" }}>
          Enter a coordinate to assess stop safety across 14 criteria including
          visibility, ADA access, railroad proximity, and road geometry.
        </Typography>

        <Divider sx={{ borderColor: "#1e1e1e", mb: 4 }} />

        <Stack spacing={2}>
          <Stack direction="row" spacing={2}>
            <TextField
              label="latitude"
              value={lat}
              onChange={e => setLat(e.target.value)}
              placeholder="40.8524"
              fullWidth
              disabled={loading}
              slotProps={{ htmlInput: { inputMode: "decimal" } }}
            />
            <TextField
              label="longitude"
              value={lng}
              onChange={e => setLng(e.target.value)}
              placeholder="-73.8506"
              fullWidth
              disabled={loading}
              slotProps={{ htmlInput: { inputMode: "decimal" } }}
            />
          </Stack>

          {error && <Alert severity="error" sx={{ borderRadius: 1 }}>{error}</Alert>}

          <Button
            variant="outlined" size="large" onClick={handleSubmit} disabled={loading}
            sx={{
              height: 52, borderColor: "#333", color: "#e8e8e8", fontSize: "0.85rem",
              "&:hover": { borderColor: "#e8e8e8", background: "rgba(255,255,255,0.03)" },
            }}
          >
            {loading ? (
              <Box sx={{ display: "flex", flexDirection: "row", alignItems: "center", gap: 1.5 }}>
                <CircularProgress size={16} sx={{ color: "#888" }} />
                <Typography sx={{ fontFamily: '"JetBrains Mono", monospace', fontSize: "0.8rem", color: "#888" }}>
                  {phase}
                </Typography>
              </Box>
            ) : "run evaluation →"}
          </Button>
        </Stack>

        <Divider sx={{ borderColor: "#1e1e1e", mt: 4, mb: 3 }} />

        <Typography variant="overline" sx={{ color: "#444", display: "block", mb: 1.5 }}>
          criteria evaluated
        </Typography>
        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
          {[
            "railroad", "slope", "freeway ramp", "traffic signal", "divided highway",
            "right turn lane", "u-turn", "bike lane", "sidewalk", "waiting area",
            "visibility", "ADA", "obstructions", "water body",
          ].map(c => (
            <Typography key={c} sx={{
              fontFamily: '"JetBrains Mono", monospace', fontSize: "0.7rem", color: "#444",
              border: "1px solid #1e1e1e", px: 1, py: 0.25, borderRadius: "2px",
            }}>
              {c}
            </Typography>
          ))}
        </Box>
      </Box>
    </Box>
  )
}
