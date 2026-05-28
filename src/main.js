// vue-contents/src/main.js
import { createApp } from 'vue'
import App from './App.vue'           // ルートはApp.vueにする
import { createPinia } from 'pinia'
import router from './router'         // ルーターをインポート
import axios from 'axios'
import './assets/css/main.css'

axios.defaults.withCredentials = true
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

const app = createApp(App)            // App.vueをベースにアプリ生成
const pinia = createPinia() // 2. Pinia インスタンスを作成

app.use(pinia)  // 3. VueアプリにPiniaを覚えさせる
app.use(router)                       // ルーターを有効化
app.mount('#app')                     // マウント
