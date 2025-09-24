import { resolve } from "path";
import { defineConfig, externalizeDepsPlugin } from "electron-vite";
import react from "@vitejs/plugin-react";
import { settings } from "./src/lib/electron-router-dom";

export default defineConfig({
  main: {
    resolve: {
      alias: {
        "@lib": resolve("src/lib"),
      },
    },
    plugins: [externalizeDepsPlugin()],
  },
  preload: {
    plugins: [externalizeDepsPlugin()],
  },
  renderer: {
    resolve: {
      alias: {
        "@renderer": resolve("src/renderer/src"),
        "@lib": resolve("src/lib"),
        "@": resolve("src"),
      },
    },
    plugins: [react()],
    server: {
      port: settings.port,
    },
    build: {
      // outDir: "out",
      // target: "esnext",
    },
  },
});
