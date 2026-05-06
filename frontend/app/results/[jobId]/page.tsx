import { notFound } from "next/navigation"
import Link from "next/link"
import { Box, Typography, Divider, Stack } from "@mui/material"
import { getEvaluation } from "@/lib/api"
import ScoreDisplay from "@/components/ScoreDisplay"
import FailuresPanel from "@/components/FailuresPanel"
import ImageGallery from "@/components/ImageGallery"

export default async function ResultsPage({ params }: { params: { jobId: string } }) {
  let result
  try {
    result = await getEvaluation(params.jobId)
  } catch {
    notFound()
  }

  return (
    <Box sx={{ minHeight: "100vh", px: { xs: 3, md: 6 }, py: 5, maxWidth: 1100, mx: "auto" }}>
      <Link href="/" style={{ textDecoration: "none" }}>
        <Typography sx={{
          fontFamily: '"JetBrains Mono", monospace', fontSize: "0.75rem",
          color: "#444", mb: 4, display: "block", "&:hover": { color: "#888" },
        }}>
          ← new evaluation
        </Typography>
      </Link>

      <Box sx={{ mb: 4 }}>
        <Typography variant="overline" sx={{ color: "#555", display: "block", mb: 0.5 }}>
          evaluation result
        </Typography>
        <Typography variant="h4" sx={{ fontWeight: 700, fontSize: { xs: "1.5rem", sm: "2rem" }, mb: 0.5 }}>
          stop assessment
        </Typography>
        <Typography sx={{ fontFamily: '"JetBrains Mono", monospace', fontSize: "0.75rem", color: "#444" }}>
          {result.snapped_lat.toFixed(6)}, {result.snapped_lng.toFixed(6)}
          &nbsp;&nbsp;·&nbsp;&nbsp;job {result.job_id}
        </Typography>
      </Box>

      <Divider sx={{ borderColor: "#1e1e1e", mb: 5 }} />

      <Box sx={{
        display: "grid",
        gridTemplateColumns: { xs: "1fr", md: "1fr 340px" },
        gap: 5,
        alignItems: "start",
      }}>
        <Stack spacing={5}>
          <ScoreDisplay score={result.score} verdict={result.verdict} />
          <FailuresPanel failures={result.failures} results={result.results} />
        </Stack>
        <Box sx={{ position: { md: "sticky" }, top: { md: 40 } }}>
          <ImageGallery imageUrls={result.image_urls} />
        </Box>
      </Box>
    </Box>
  )
}
