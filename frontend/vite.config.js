import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    // PWA 配置（阶段 5 会细化）
    VitePWA({
      registerType: 'auto',
      includeAssets: ['favicon.ico'],
      manifest: {
        name: '智药通',
        short_name: '智药通',
        description: 'AI 老年人用药安全助手',
        theme_color: '#1989fa',
        background_color: '#ffffff',
        display: 'standalone',
        start_url: '/',
        icons: [
          {
            src: 'pwa-icons/192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'pwa-icons/512.png',
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      }
    })
  ],
  server: {
    port: 5173,
    host: true // 允许局域网访问，方便手机调试
  }
})