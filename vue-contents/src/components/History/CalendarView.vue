<template>
    <div class="history">
        <!--dailyHistory にデータが入ってから描画する-->
        <WeeklyProgress v-if="dailyHistory.length" :dailyHistory="dailyHistory" />
        <DailyExerciseHistory v-if="dailyHistory.length" :dailyHistory="dailyHistory" />
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import WeeklyProgress from './WeeklyProgress.vue'
  import DailyExerciseHistory from './DailyExerciseHistory.vue'
  
  const dailyHistory = ref([])
  
  async function fetchExerciseHistory() {
    try {
      // 絶対URLに修正
      const apiUrl = 'http://127.0.0.1:8000/exercise/api/logs/list/'
      console.log('Fetching API URL:', apiUrl)
  
      const res = await fetch(apiUrl, { credentials: 'include' })
      if (!res.ok) throw new Error(`fetch failed: ${res.status}`)
      const data = await res.json()
      console.log('Fetched daily history:', data)
  
      // 日付ごとにグルーピング
      const grouped = data.reduce((acc, log) => {
        const date = log.date
        if (!acc[date]) {
          acc[date] = { date, exercises: [], doneCount: 0, totalCount: 0 }
        }
        acc[date].exercises.push(log.exercises ?? log.exercise_name ?? log.exercise)
        acc[date].doneCount += log.done_count ?? 1
        acc[date].totalCount += log.total_count ?? 1
        return acc
      }, {})
  
      // 配列に変換して日付降順
      dailyHistory.value = Object.values(grouped).sort((a, b) => b.date.localeCompare(a.date))
      console.log('Grouped dailyHistory:', dailyHistory.value)
    } catch (err) {
      console.error('CalendarView: fetchExerciseHistory error', err)
    }
  }
  
  onMounted(fetchExerciseHistory)
  </script>
  
  <style>
  .history {
  background-color: #fff;
}

  </style>