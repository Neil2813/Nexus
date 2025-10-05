import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{ts,tsx,js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: { DEFAULT: "hsl(var(--primary))", foreground: "hsl(var(--primary-foreground))" },
        secondary: { DEFAULT: "hsl(var(--secondary))", foreground: "hsl(var(--secondary-foreground))" },
        destructive: { DEFAULT: "hsl(var(--destructive))", foreground: "hsl(var(--destructive-foreground))" },
        muted: { DEFAULT: "hsl(var(--muted))", foreground: "hsl(var(--muted-foreground))" },
        accent: { DEFAULT: "hsl(var(--accent))", foreground: "hsl(var(--accent-foreground))" },
        popover: { DEFAULT: "hsl(var(--popover))", foreground: "hsl(var(--popover-foreground))" },
        card: { DEFAULT: "hsl(var(--card))", foreground: "hsl(var(--card-foreground))" },
        mlpurple: { DEFAULT: "hsl(var(--ml-purple))", foreground: "hsl(var(--ml-purple-foreground))" },
        nebula: { DEFAULT: "hsl(var(--nebula))", foreground: "hsl(var(--nebula-foreground))" },
        solar: { DEFAULT: "hsl(var(--solar))", foreground: "hsl(var(--solar-foreground))" },
        mars: { DEFAULT: "hsl(var(--mars))", foreground: "hsl(var(--mars-foreground))" },
        // NEXUS Theme Colors - Based on Logo
        space: "hsl(0, 0%, 0%)",           // Pure black background (from logo)
        spacestation: "hsl(200, 100%, 10%)", // Very dark cyan
        astronautwhite: "hsl(180, 100%, 98%)", // Cyan-tinted white
        mission: "hsl(190, 100%, 50%)",     // Bright cyan (logo color)
        neural: "hsl(190, 100%, 50%)",      // Cyan accent (#00D9FF)
        nexuscyan: "hsl(190, 100%, 50%)",   // Primary cyan from logo
        darkspace: "hsl(200, 50%, 5%)",     // Very dark blue-black
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [],
};

export default config;
