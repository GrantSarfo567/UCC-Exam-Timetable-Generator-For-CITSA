/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ucc: {
          blue:      "#1A3A6B",
          blueDark:  "#122850",
          blueLight: "#2A5298",
          red:       "#CC0000",
          gold:      "#FFD700",
          goldDark:  "#C9A800",
          white:     "#FFFFFF",
          gray:      "#F4F6F9",
          border:    "#DDE3ED",
          text:      "#1A1A2E",
          muted:     "#6B7280",
        },
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
      },
    },
  },
  plugins: [],
}