<template>
    <div class="daily-history">
      <h2>年間運動履歴</h2>
      <div class="chart-wrapper">
        <BarChart ref="barRef" :data="annualChartData" :options="chartOptions" />
      </div>
  
      <!-- モーダル -->
      <div v-if="showModal" class="modal-backdrop" @click.self="showModal = false">
        <div class="modal">
          <h3>{{ selectedLabel }} の詳細</h3>
          <ul>
            <li v-for="item in selectedData" :key="item.date">
              {{ item.date }} - 完了: {{ item.doneCount }}/{{ item.totalCount }}
              <ul>
                <li v-for="ex in item.exercises" :key="ex">{{ ex }}</li>
              </ul>
            </li>
          </ul>
          <button @click="showModal = false">閉じる</button>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
import { ref, onMounted, computed } from 'vue'
import { Bar as BarChart } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js'
ChartJS.register(Title, Tooltip, Legend, CategoryScale, LinearScale, BarElement)

const props = defineProps({ dailyHistory: Array })

const annualChartData = computed(() => {
  const monthTotals = Array(12).fill(0)
  props.dailyHistory.forEach(day => {
    const monthIndex = new Date(day.date).getMonth()
    monthTotals[monthIndex] += day.doneCount
  })
  return {
    labels: ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'],
    datasets: [{ label: '月別完了数', data: monthTotals, backgroundColor: '#4ade80' }]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: { y: { beginAtZero: true } }
}

const showModal = ref(false)
const selectedLabel = ref('')
const selectedData = ref([])

const barRef = ref()

onMounted(() => {
  // vue-chartjsのchartインスタンスがまだ存在しないことがあるのでチェックする
  if (!barRef.value || !barRef.value.chart) {
    console.warn('barRef.chart がまだ初期化されていません')
    return
  }

  const chart = barRef.value.chart
  if (!chart.canvas) {
    console.warn('chart.canvas がありません')
    return
  }

  chart.canvas.onclick = evt => {
    const points = chart.getElementsAtEventForMode(evt, 'nearest', { intersect: true }, true)
    if (!points.length) return
    const index = points[0].index
    const label = annualChartData.value.labels[index]
    selectedLabel.value = label
    const monthIndex = index
    selectedData.value = props.dailyHistory.filter(
      d => new Date(d.date).getMonth() === monthIndex
    )
    showModal.value = true
  }
})
</script>

  
  <style scoped>
  .daily-history { border: 1px solid #ccc; padding: 10px; }
  .chart-wrapper { height: 300px; }
  
  .modal-backdrop {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.5);
    display: flex; align-items: center; justify-content: center;
  }
  .modal {
    background: white;
    padding: 1rem;
    max-height: 80vh;
    overflow-y: auto;
    border-radius: 8px;
    width: 400px;
  }
  </style>
  