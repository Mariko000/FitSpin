import { createRouter, createWebHistory } from 'vue-router'
import MainContent from '../components/MainContent.vue' // メインコンテンツコンポーネントをインポート
import About from '../components/About.vue' // Aboutページコンポーネントをインポート

const routes = [
  {
    path: '/',
    name: 'Home',
    component: MainContent
  },
  {
    path: '/about',
    name: 'About',
    component: About
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
