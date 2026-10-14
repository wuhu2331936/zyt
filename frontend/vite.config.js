import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { VitePWA } from "vite-plugin-pwa";
import { fileURLToPath, URL } from "node:url";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      // 比赛场景默认 autoUpdate，用户无需手动刷新即可拿到新版本
      registerType: "autoUpdate",

      // manifest 选项会自动生成 manifest.webmanifest
      // 也可以用 filename 指向独立的 manifest.webmanifest 文件
      manifest: false,
      // 指向已写好的 manifest 文件（包含中文名称、截图等）
      manifestFilename: "manifest.webmanifest",

      // Service Worker 缓存策略
      workbox: {
        // 预缓存列表（globPatterns 默认会包含 html/css/js）
        globPatterns: ["**/*.{js,css,html,ico,png,svg,webmanifest}"],
        // 不预缓存超过 2 MB 的资源（Hugging Face 模型文件等）
        maximumFileSizeToCacheInBytes: 2 * 1024 * 1024,

        // 运行时缓存策略
        runtimeCaching: [
          {
            // 百度 / 谷歌字体（如果用了）
            urlPattern: /^https:\/\/fonts\.(?:googleapis|gstatic)\.com\//,
            handler: "CacheFirst",
            options: {
              cacheName: "google-fonts",
              expiration: { maxEntries: 30, maxAgeSeconds: 60 * 60 * 24 * 365 },
            },
          },
          {
            // 后端 API —— 网络优先（在线实时，离线兜底用最后一次的响应）
            urlPattern: /\/api\/.*/,
            handler: "NetworkFirst",
            options: {
              cacheName: "api-cache",
              networkTimeoutSeconds: 5,
              expiration: { maxEntries: 50, maxAgeSeconds: 60 * 5 },
            },
          },
          {
            // 图片资源 —— 缓存优先（药盒照片等）
            urlPattern: /\.(?:png|jpg|jpeg|svg|gif|webp)$/,
            handler: "CacheFirst",
            options: {
              cacheName: "images",
              expiration: { maxEntries: 60, maxAgeSeconds: 60 * 60 * 24 * 30 },
            },
          },
        ],
      },

      // 注入一个虚拟模块，让前端检测 PWA 状态
      injectRegister: "auto",
      devOptions: {
        // 开发模式下也启用（方便调试）
        enabled: false,
        type: "module",
      },
    }),
  ],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    host: "0.0.0.0",
    port: 5173,
    // PWA 必须在 https 或 localhost 才生效——开发环境 localhost 自动 ok
  },
});
