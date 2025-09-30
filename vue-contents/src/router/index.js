// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import MainContent from '../components/MainContent.vue'
import ExerciseDone from '../components/ExerciseDone.vue'
import CalendarView from '../components/History/CalendarView.vue'
import ExerciseLogList from '../components/History/ExerciseLogList.vue'

const routes = [
  { path: '/', component: MainContent },
  { path: '/exercise-done', component: ExerciseDone },
  { path: '/calendar', component: CalendarView },
  {
    path: '/exercise-logs/month/:yearMonth',
    name: 'exercise_logs_by_month',
    component: ExerciseLogList
  },
  
  
  //キャッチオールは最後に置く
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

export default createRouter({
  // ベースURLを明示的に設定
  history: createWebHistory('/'),
  routes
})