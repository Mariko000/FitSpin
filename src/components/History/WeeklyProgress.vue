<template>
  <div class="weekly-progress">
    <!-- 月間運動履歴タイトルをリンク化 -->
    <router-link
  :to="{ name: 'exercise_logs_by_month', params: { yearMonth: currentYearMonth } }"
  class="month-link"
>
  <h2>{{ currentMonthLabel }}月間運動履歴</h2>
</router-link>


    <!-- 月間グラフ -->
    <div class="chart-wrapper">
      <BarChart ref="barRef" :data="monthlyChartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement
} from 'chart.js'
import { Bar as BarChart } from 'vue-chartjs'

ChartJS.register(Title, Tooltip, Legend, CategoryScale, LinearScale, BarElement)

const props = defineProps({
  dailyHistory: { type: Array, required: true }
})

const barRef = ref(null)

// 当月ラベル（例：9月）
const currentMonthLabel = computed(() => {
  const now = new Date()
  return now.getMonth() + 1
})

// URL 用の yearMonth（例: "2025-09"）
const currentYearMonth = computed(() => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  return `${year}-${month}`
})

// 直近1ヶ月のデータをグラフ用に
const monthlyChartData = computed(() => {
  const now = new Date()
  const oneMonthAgo = new Date()
  oneMonthAgo.setMonth(now.getMonth() - 1)

  const filtered = props.dailyHistory.filter(
    day => new Date(day.date) >= oneMonthAgo
  )

  const labels = filtered.map(d => new Date(d.date).getDate())
  const data = filtered.map(d => d.doneCount)

  return {
    labels,
    datasets: [{
      label: '日別完了数（直近1ヶ月）',
      data,
      backgroundColor: '#60a5fa',
      borderColor: '#2563eb',
      borderWidth: 1
    }]
  }
})

// Chart.js のオプション
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: { x: { type: 'category' }, y: { beginAtZero: true } }
}
</script>

<style scoped>
.weekly-progress {
  border: 1px solid #ccc;
  padding: 10px;
}
.chart-wrapper {
  height: 300px;
  width: 100%;
}
.month-link h2 {
  cursor: pointer;
  color: #2563eb;
  text-decoration: underline;
}
</style>
