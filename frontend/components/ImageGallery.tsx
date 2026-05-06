"use client"

import { useState } from "react"
import { Box, Typography } from "@mui/material"
import Image from "next/image"
import { imageUrl } from "@/lib/api"

const DIRECTION_LABEL: Record<string, string> = {
  n: "north", s: "south", e: "east", w: "west",
  fwd_n: "fwd north", fwd_s: "fwd south",
  bwd_n: "bwd north", bwd_s: "bwd south",
}

function getLabel(url: string): string {
  const match = url.match(/_([a-z_]+)\.jpg$/)
  return match ? (DIRECTION_LABEL[match[1]] ?? match[1]) : ""
}

export default function ImageGallery({ imageUrls }: { imageUrls: string[] }) {
  const [selected, setSelected] = useState(0)
  if (!imageUrls.length) return null

  return (
    <Box>
      <Typography variant="overline" sx={{ color: "#555", display: "block", mb: 2 }}>
        street view imagery
      </Typography>

      <Box sx={{
        position: "relative", width: "100%", aspectRatio: "1 / 1",
        background: "#111", border: "1px solid #1e1e1e",
        borderRadius: "2px", overflow: "hidden", mb: 1.5,
      }}>
        <Image
          src={imageUrl(imageUrls[selected])}
          alt={`Street view ${getLabel(imageUrls[selected])}`}
          fill style={{ objectFit: "cover" }} unoptimized
        />
        <Box sx={{ position: "absolute", bottom: 8, left: 8, background: "rgba(0,0,0,0.7)", px: 1, py: 0.25, borderRadius: "2px" }}>
          <Typography sx={{ fontFamily: '"JetBrains Mono", monospace', fontSize: "0.7rem", color: "#888" }}>
            {getLabel(imageUrls[selected])}
          </Typography>
        </Box>
      </Box>

      <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
        {imageUrls.map((url, i) => (
          <Box key={url} onClick={() => setSelected(i)} sx={{
            position: "relative", width: 64, height: 64,
            border: i === selected ? "1px solid #e8e8e8" : "1px solid #1e1e1e",
            borderRadius: "2px", overflow: "hidden", cursor: "pointer",
            flexShrink: 0, opacity: i === selected ? 1 : 0.5,
            transition: "opacity 0.15s, border-color 0.15s",
            "&:hover": { opacity: 1 },
          }}>
            <Image src={imageUrl(url)} alt={getLabel(url)} fill style={{ objectFit: "cover" }} unoptimized />
          </Box>
        ))}
      </Box>
    </Box>
  )
}
