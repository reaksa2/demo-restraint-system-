import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "https://restaurant-api-demo.onrender.com",
        changeOrigin: true,
        secure: true,
      },
      "/static": {
        target: "https://restaurant-api-demo.onrender.com",
        changeOrigin: true,
        secure: true,
      },
    },
  },
});
