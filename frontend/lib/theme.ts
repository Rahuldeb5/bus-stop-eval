"use client"

import { createTheme } from "@mui/material/styles"

export const theme = createTheme({
  palette: {
    mode: "dark",
    background: { default: "#080808", paper: "#111111" },
    primary:    { main: "#e8e8e8" },
    error:      { main: "#ef4444" },
    warning:    { main: "#f97316" },
    success:    { main: "#22c55e" },
    text:       { primary: "#e8e8e8", secondary: "#888888" },
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
        root: { textTransform: "none", fontFamily: '"JetBrains Mono", monospace', letterSpacing: "0.05em", borderRadius: 2 },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          "& .MuiOutlinedInput-root": {
            fontFamily: '"JetBrains Mono", monospace', borderRadius: 2,
            "& fieldset": { borderColor: "#333" },
            "&:hover fieldset": { borderColor: "#555" },
            "&.Mui-focused fieldset": { borderColor: "#e8e8e8" },
          },
        },
      },
    },
    MuiPaper: { styleOverrides: { root: { backgroundImage: "none" } } },
  },
})
