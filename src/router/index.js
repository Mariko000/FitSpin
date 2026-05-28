// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import MainContent from '../components/MainContent.vue'
import ExerciseDone from '../components/ExerciseDone.vue'
import StampCard from '../components/StampCard.vue'
import ExerciseLogList from '../components/History/ExerciseLogList.vue'
import StampCollection from '../components/Stamp_Collection.vue'


const routes = [
  { path: '/', component: MainContent },
  { path: '/exercise-done', component: ExerciseDone },
  { path: '/StampCard', component: StampCard },
  {
    path: '/exercise-logs',
    component: ExerciseLogList
  },
  {
    path: '/StampCollection',
    component: StampCollection
  },
  
  
  //キャッチオールは最後に置く
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

export default createRouter({
  // ベースURLを明示的に設定
  history: createWebHistory('/'),
  routes
})