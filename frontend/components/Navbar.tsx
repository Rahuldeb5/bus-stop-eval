"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Box, Typography, IconButton } from "@mui/material"
import { useThemeMode } from "../lib/ThemeContext"

export default function Navbar() {
  const path = usePathname()
  const { mode, toggle } = useThemeMode()

  const links = [
    { href: "/",        label: "evaluate" },
    { href: "/history", label: "history"  },
  ]

  const navBg   = mode === "dark" ? "rgba(8,8,8,0.85)"   : "rgba(245,245,245,0.85)"
  const border  = mode === "dark" ? "#1a1a1a"             : "#e0e0e0"
  const active  = mode === "dark" ? "#e8e8e8"             : "#111111"
  const inactive = mode === "dark" ? "#444"               : "#aaaaaa"

  return (
    <Box
      component="nav"
      sx={{
        position:       "fixed",
        top:            0,
        left:           0,
        right:          0,
        zIndex:         100,
        display:        "flex",
        alignItems:     "center",
        justifyContent: "space-between",
        px:             { xs: 3, md: 5 },
        py:             2,
        borderBottom:   `1px solid ${border}`,
        background:     navBg,
        backdropFilter: "blur(12px)",
      }}
    >
      <Link href="/" style={{ textDecoration: "none" }}>
        <Typography sx={{
          fontFamily:    '"JetBrains Mono", monospace',
          fontSize:      "0.8rem",
          fontWeight:    700,
          color:         active,
          letterSpacing: "0.05em",
        }}>
          stop evaluator
        </Typography>
      </Link>

      <Box sx={{ display: "flex", alignItems: "center", gap: 3 }}>
        {links.map(({ href, label }) => (
          <Link key={href} href={href} style={{ textDecoration: "none" }}>
            <Typography sx={{
              fontFamily:    '"JetBrains Mono", monospace',
              fontSize:      "0.75rem",
              color:         path === href || (href !== "/" && path.startsWith(href))
                               ? active : inactive,
              letterSpacing: "0.05em",
              transition:    "color 0.15s",
            }}>
              {label}
            </Typography>
          </Link>
        ))}

        <IconButton onClick={toggle} size="small" sx={{ color: inactive, p: 0.5 }}>
          <Typography sx={{ fontFamily: '"JetBrains Mono", monospace', fontSize: "0.75rem" }}>
            {mode === "dark" ? "☀" : "☾"}
          </Typography>
        </IconButton>
      </Box>
    </Box>
  )
}
