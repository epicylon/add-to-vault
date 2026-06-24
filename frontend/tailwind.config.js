/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive) / <alpha-value>)",
          foreground: "hsl(var(--destructive-foreground) / <alpha-value>)",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        sidebar: {
          DEFAULT: "hsl(var(--sidebar-background))",
          foreground: "hsl(var(--sidebar-foreground))",
          primary: "hsl(var(--sidebar-primary))",
          "primary-foreground": "hsl(var(--sidebar-primary-foreground))",
          accent: "hsl(var(--sidebar-accent))",
          "accent-foreground": "hsl(var(--sidebar-accent-foreground))",
          border: "hsl(var(--sidebar-border))",
          ring: "hsl(var(--sidebar-ring))",
        },
        obsidian: {
          base: "#050507",
          surface: "#0c0c0f",
          elevated: "#141419",
          overlay: "#1a1a22",
          "border-subtle": "#1e1e28",
          "border-medium": "#2a2a38",
          "border-accent": "#5b4cdb",
          "text-primary": "#f0f0f5",
          "text-secondary": "#8a8a9e",
          "text-muted": "#555568",
        },
        vault: {
          accent: "#6c5ce7",
          "accent-hover": "#7c6ff0",
          success: "#34d399",
          error: "#f87171",
          warning: "#fbbf24",
          "admin-badge": "#a78bfa",
        },
      },
      fontFamily: {
        sans: ['"Inter"', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"SF Mono"', '"Fira Code"', 'monospace'],
      },
      borderRadius: {
        xl: "calc(var(--radius) + 4px)",
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
        xs: "calc(var(--radius) - 6px)",
      },
      boxShadow: {
        xs: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
        "vault-card": "0 1px 3px rgba(0,0,0,0.3), 0 0 0 1px #1e1e28",
        "vault-elevated": "0 4px 24px rgba(0,0,0,0.4), 0 0 0 1px #1e1e28",
        "vault-glow": "0 0 20px rgba(108, 92, 231, 0.15)",
        "vault-inner": "inset 0 1px 2px rgba(0,0,0,0.2)",
        "vault-focus": "0 0 0 3px rgba(108, 92, 231, 0.15)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
        "caret-blink": {
          "0%,70%,100%": { opacity: "1" },
          "20%,50%": { opacity: "0" },
        },
        "spin-loader": {
          to: { transform: "rotate(360deg)" },
        },
        "toast-in": {
          from: { opacity: "0", transform: "translateY(-6px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        "toast-out": {
          from: { opacity: "1", transform: "translateY(0)" },
          to: { opacity: "0", transform: "translateY(-6px)" },
        },
        "fade-in-up": {
          from: { opacity: "0", transform: "translateY(12px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        "fade-out-up": {
          from: { opacity: "1", transform: "translateY(0)" },
          to: { opacity: "0", transform: "translateY(-8px)" },
        },
        "pop-check": {
          "0%": { transform: "scale(0.8)" },
          "50%": { transform: "scale(1.1)" },
          "100%": { transform: "scale(1)" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "caret-blink": "caret-blink 1.25s ease-out infinite",
        "spin-loader": "spin-loader 0.7s linear infinite",
        "toast-in": "toast-in 0.3s ease-out",
        "toast-out": "toast-out 0.3s ease-in",
        "fade-in-up": "fade-in-up 0.4s ease-out",
        "fade-out-up": "fade-out-up 0.25s ease-in",
        "pop-check": "pop-check 0.3s ease",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}