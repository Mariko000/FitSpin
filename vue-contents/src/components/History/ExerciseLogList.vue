<template>
    <div>
      <h1>{{ yearMonth }} の運動ログ</h1>
      <ul>
        <li v-for="log in logs" :key="log.id">
          {{ log.date }} - {{ log.exercise_name }} - {{ log.duration }}
        </li>
      </ul>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { useRoute } from 'vue-router'
  
  const route = useRoute()
  const yearMonth = route.params.yearMonth
  const logs = ref([])
  
  onMounted(async () => {
    // ひとまず全部取ってくる
    const res = await fetch('http://127.0.0.1:8000/exercise/api/logs/list/', {
      credentials: 'include'
    })
    const data = await res.json()
    logs.value = data
  })
  </script>
  