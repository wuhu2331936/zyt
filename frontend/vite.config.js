import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { VitePWA } from "vite-plugin-pwa";
import { fileURLToPath, URL } from "node:url";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      // ⚠️ selfDestroying：生成的 sw.js 只做一件事——注销旧 SW 并清空缓存。
      // 比赛期间代码频繁更新，若用 workbox 预缓存，手机/老师浏览器会拿到旧资源
      // （曾导致"页面白屏/旧样式"反复复现）。关掉缓存保证每次部署都是最新代码。
      selfDestroying: true,

      // manifest 选项会自动生成 manifest.webmanifest
      // 也可以用 filename 指向独立的 manifest.webmanifest 文件
      manifest: false,
      // 指向已写好的 manifest 文件（包含中文名称、截图等）
      manifestFilename: "manifest.webmanifest",

      // Service Worker 缓存策略（selfDestroying 为 true 时以下配置不生效，保留备用）
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
    // 同源 /api 转发到后端：手机访问时也能正常调用 AI 接口
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
    // PWA 必须在 https 或 localhost 才生效——开发环境 localhost 自动 ok
  },
  preview: {
    host: "0.0.0.0",
    port: 4173,
    // preview（生产构建静态托管）同样需要转发，否则 /api 404
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});
