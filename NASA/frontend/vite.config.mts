import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve("./src"), // Now you can import using "@/components/..."
    },
  },
  server: {
    port: 5173, // Change port if needed
    strictPort: true,
  },
  css: {
    postcss: "./postcss.config.mjs", // Ensure Vite uses your PostCSS config
  },
});
