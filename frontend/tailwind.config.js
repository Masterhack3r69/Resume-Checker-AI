export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      colors: {
        background: "#020617", // Slate 950 (V. Dark)
        surface: "#0f172a", // Slate 900
        surfaceHighlight: "#1e293b", // Slate 800
        primary: "#6366f1", // Indigo 500
        primaryHover: "#4f46e5", // Indigo 600
        secondary: "#64748b",
        success: "#10b981", // Emerald 500
        warning: "#f59e0b", // Amber 500
        danger: "#ef4444", // Red 500
      },
      animation: {
        blob: "blob 7s infinite",
        "fade-in": "fadeIn 0.5s ease-out forwards",
        "slide-up": "slideUp 0.5s ease-out forwards",
      },
      keyframes: {
        blob: {
          "0%": { transform: "translate(0px, 0px) scale(1)" },
          "33%": { transform: "translate(30px, -50px) scale(1.1)" },
          "66%": { transform: "translate(-20px, 20px) scale(0.9)" },
          "100%": { transform: "translate(0px, 0px) scale(1)" },
        },
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { transform: "translateY(20px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
      },
      backdropBlur: {
        xs: "2px",
      },
    },
  },
  plugins: [],
};
