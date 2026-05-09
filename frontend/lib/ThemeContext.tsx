"use client"

import { createContext, useContext, useState, ReactNode } from "react"
import { ThemeProvider } from "@mui/material/styles"
import { createTheme } from "@mui/material/styles"

const getTheme = (mode: "dark" | "light") => createTheme({
  palette: {
    mode,
    background: {
      default: mode === "dark" ? "#080808" : "#f5f5f5",
      paper:   mode === "dark" ? "#111111" : "#ffffff",
    },
    primary:   { main: mode === "dark" ? "#e8e8e8" : "#111111" },
    error:     { main: "#ef4444" },
    warning:   { main: "#f97316" },
    success:   { main: "#22c55e" },
    text: {
      primary:   mode === "dark" ? "#e8e8e8" : "#111111",
      secondary: mode === "dark" ? "#888888" : "#666666",
    },
  },
  typography: {
    fontFamily: '"IBM Plex Sans", sans-serif',
    h1: { fontFamily: '"JetBrains Mono", monospace', letterSpacing: "-0.03em" },
    h2: { fontFamily: '"JetBrains Mono", monospace', letterSpacing: "-0.02em" },
    h3: { fontFamily: '"JetBrains Mono", monospace' },
    h4: { fontFamily: '"JetBrains Mono", monospace' },
    h5: { fontFamily: '"JetBrains Mono", monospace' },
    h6: { fontFamily: '"JetBrains Mono", monospace' },
    overline: { fontFamily: '"JetBrains Mono", monospace', letterSpacing: "0.15em" },
  },
  shape: { borderRadius: 2 },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: "none",
          fontFamily: '"JetBrains Mono", monospace',
          letterSpacing: "0.05em",
          borderRadius: 2,
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          "& .MuiOutlinedInput-root": {
            fontFamily: '"JetBrains Mono", monospace',
            borderRadius: 2,
            "& fieldset": { borderColor: mode === "dark" ? "#333" : "#ccc" },
            "&:hover fieldset": { borderColor: mode === "dark" ? "#555" : "#999" },
            "&.Mui-focused fieldset": { borderColor: mode === "dark" ? "#e8e8e8" : "#111" },
          },
        },
      },
    },
    MuiPaper: { styleOverrides: { root: { backgroundImage: "none" } } },
  },
})

const ThemeModeContext = createContext({
  mode: "dark" as "dark" | "light",
  toggle: () => {},
})

export function useThemeMode() {
  return useContext(ThemeModeContext)
}

export function ThemeModeProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<"dark" | "light">("dark")
  const toggle = () => setMode(m => m === "dark" ? "light" : "dark")

  return (
    <ThemeModeContext.Provider value={{ mode, toggle }}>
      <ThemeProvider theme={getTheme(mode)}>
        {children}
      </ThemeProvider>
    </ThemeModeContext.Provider>
  )
}
