import type { Metadata } from "next"
import { AppRouterCacheProvider } from "@mui/material-nextjs/v15-appRouter"
import CssBaseline from "@mui/material/CssBaseline"
import Navbar from "@/components/Navbar"
import { Box } from "@mui/material"
import { ThemeModeProvider } from "../lib/ThemeContext"

export const metadata: Metadata = {
  title: "Bus Stop Evaluator",
  description: "Safety evaluation for school bus stop locations",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@300;400;500;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <AppRouterCacheProvider>
          <ThemeModeProvider>
            <CssBaseline />
            <Navbar />
            <Box sx={{ pt: "57px" }}>{children}</Box>
          </ThemeModeProvider>
        </AppRouterCacheProvider>
      </body>
    </html>
  )
}
