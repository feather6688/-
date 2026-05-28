import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Vite 配置文件
// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,                // 开发服务器端口
    open: true,                // 启动时自动打开浏览器
    proxy: {
      // 将 /api 开头的请求代理到 Python 后端（备用，本项目主要用 WebSocket）
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
