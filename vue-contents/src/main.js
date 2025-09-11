import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // ルーターをインポート

const app = createApp(App)
app.use(router) // アプリケーションでルーターを使用
app.mount('#app')
