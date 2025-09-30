<template>
  <div class="gacha-container">
    <h2 style="color: black;">今日の運動は何かな？ガチャを引いてみよう</h2>

    <div class="gacha-area" style="position: relative; height: 300px;">
      <div class="machine-wrapper" :class="{ shake: shaking, fadeOut: machineOut }" v-show="!showResult">
        <img class="gacha-machine" :src="gachaMachine" alt="ガチャマシーン" />
        <img class="capsule" :class="{ show: capsuleVisible, out: capsuleOut }" :src="capsule" alt="カプセル" />
      </div>

      <div v-if="showResult" class="exercise-card" 
           style="position: absolute; top: 0; left: 50%; transform: translateX(-50%); width: 100%;">
        <p class="exercise-name">{{ exerciseResult.name }}</p>
        <p class="exercise-level">レベル: {{ exerciseResult.level }}</p>
        <p class="exercise-description">{{ exerciseResult.description }}</p>
      </div>
    </div>

    <p v-if="loading" class="loading-message">読み込み中...</p>
    <p v-if="error" class="error-message">{{ error }}</p>

    <div class="button-container">
      <button @click="drawGacha" :disabled="drawing || loading" class="gacha-button">
        {{ exerciseResult ? 'もう一度ガチャを引く' : 'ガチャを引く' }}
      </button>
      <button @click="handleDone" :disabled="!exerciseResult || sending" class="gacha-button">
        やった！
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import gachaMachine from '../assets/images/gacha_machine.png'
import capsule from '../assets/images/capsule.png'

const user = ref(null)
const loading = ref(false)
const error = ref(null)
const exerciseResult = ref(null)
const pendingResult = ref(null)
const showResult = ref(false)
const drawing = ref(false)
const sending = ref(false)

const shaking = ref(false)
const capsuleVisible = ref(false)
const capsuleOut = ref(false)
const machineOut = ref(false)

const router = useRouter()
axios.defaults.withCredentials = true

function getCSRFToken() {
  const value = `; ${document.cookie}`
  const parts = value.split(`; csrftoken=`)
  if (parts.length === 2) return parts.pop().split(';').shift()
  return null
}

async function fetchCurrentUser() {
  try {
    const csrftoken = getCSRFToken()
    const res = await axios.get('http://127.0.0.1:8000/api/users/current-user/', {
      headers: { 'X-CSRFToken': csrftoken },
      withCredentials: true
    })
    user.value = {
      ...res.data,
      avatar: res.data.avatar ? `http://127.0.0.1:8000${res.data.avatar}` : null
    }
  } catch (err) {
    error.value = 'ユーザー情報取得に失敗しました'
    console.error(err)
  }
}
onMounted(fetchCurrentUser)

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

const drawGacha = async () => {
  if (drawing.value) return
  drawing.value = true
  loading.value = true
  error.value = null

  if (!user.value) {
    error.value = 'ユーザー情報を取得中です。少し待ってから再度クリックしてください'
    loading.value = false
    drawing.value = false
    return
  }

  // 初期化
  exerciseResult.value = null
  pendingResult.value = null
  showResult.value = false
  capsuleVisible.value = false
  capsuleOut.value = false
  machineOut.value = false
  shaking.value = true

  try {
    const res = await axios.get('http://127.0.0.1:8000/exercise/api/bonus-gacha/', {
      withCredentials: true,
      headers: { 'X-CSRFToken': getCSRFToken() },
      timeout: 5000
    })
    pendingResult.value = res.data
  } catch (err) {
    error.value = err.response?.data?.detail || 'ガチャ取得中にエラーが発生しました'
    console.error(err)
    shaking.value = false
    loading.value = false
    drawing.value = false
    return
  }

  // --- 演出開始 ---
  try {
    // 少し待ってからカプセルを表示
    await sleep(500)
    capsuleVisible.value = true

    // 少し待ってからマシンの揺れを止める
    await sleep(500)
    shaking.value = false
    loading.value = false

    // カプセルを飛ばす
    await sleep(2000)
    capsuleOut.value = true

    await sleep(500)
    capsuleVisible.value = false
    capsuleOut.value = false
    machineOut.value = true

    await sleep(500)
    exerciseResult.value = pendingResult.value
    showResult.value = true
    machineOut.value = false
  } catch (err) {
    console.error('演出中にエラー:', err)
    error.value = '演出中にエラーが発生しました'
  } finally {
    drawing.value = false
  }
}

const handleDone = async () => {
  if (!exerciseResult.value || sending.value) return
  sending.value = true

  const now = new Date()
  const exerciseData = {
    exercise: exerciseResult.value.id,
    date: now.toISOString().split('T')[0],
    time: now.toTimeString().split(' ')[0],
    from_gacha: true //
  }

  try {
    await axios.post('/exercise/api/logs/', exerciseData, {
      headers: { 'X-CSRFToken': getCSRFToken() },
      withCredentials: true
    })
    alert('サーバーに記録しました！')
  } catch (err) {
    console.error(err)
    alert('サーバーへの保存に失敗しました。オフライン時はlocalStorageに残ります')
  }

  const logsByDate = JSON.parse(localStorage.getItem('exerciseLog') || '{}')
  if (!logsByDate[exerciseData.date]) logsByDate[exerciseData.date] = []
  logsByDate[exerciseData.date].push(exerciseData)
  localStorage.setItem('exerciseLog', JSON.stringify(logsByDate))

  sending.value = false
  router.push('/exercise-done')
}
</script>


<style scoped>
/* （以前と同じスタイル） */
.gacha-container { max-width: 500px; margin: 50px auto; padding: 30px; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); background-color: #f9f9f9; text-align: center; }
.avatar-img { width: 60px; height: 60px; border-radius: 50%; margin-left: 10px; vertical-align: middle; }
.gacha-button { padding: 15px 30px; margin: 10px 5px; background-color: #007bff; color: white; border: none; border-radius: 25px; font-size: 1.2em; cursor: pointer; transition: background-color 0.3s ease, transform 0.1s ease; box-shadow: 0 4px 8px rgba(0,123,255,0.3); }
.button-container { display: flex; justify-content: center; align-items: center; gap: 10px; margin-top: 20px; }
.gacha-button:hover:not(:disabled) { background-color: #0056b3; transform: translateY(-2px); }
.gacha-button:active:not(:disabled) { transform: translateY(0); box-shadow: 0 2px 4px rgba(0,123,255,0.3); }
.gacha-button:disabled { background-color: #cccccc; cursor: not-allowed; box-shadow: none; }
.loading-message { color: #007bff; font-weight:bold; }
.error-message { color: #dc3545; font-weight:bold; }
.exercise-card { margin-top: 30px; padding: 20px; }
.exercise-name { font-size:1.8em; color:#28a745; font-weight:bold; margin-bottom:10px; }
.exercise-level { font-size:1.2em; color:#6c757d; margin-bottom:20px; }
.exercise-description { font-size:1em; color:#333; }

.machine-wrapper { position: relative; display: inline-block; transition: opacity 0.5s ease; }
.machine-wrapper.shake {
  animation: shakeAnim 0.6s infinite;
  transform-origin: bottom center;
}

.gacha-machine { width: 250px; }
/* カプセルアニメーション */
.capsule {
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 80px;
  opacity: 0;
  transform: translateX(-50%) translateY(20px) scale(0.8);
  transition: opacity 0.5s ease, transform 0.7s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.capsule.show {
  opacity: 1;
  transform: translateX(-50%) translateY(-40px) scale(1.05);
}

.capsule.out {
  opacity: 0;
  transform: translateX(-50%) translateY(60px) scale(0.8);
}


.shake { animation: shakeAnim 0.3s infinite; }
@keyframes shakeAnim {
  0% { transform: translateX(0) scale(1); }
  20% { transform: translateX(-4px) scale(0.98); }
  40% { transform: translateX(4px) scale(1.02); }
  60% { transform: translateX(-3px) scale(1); }
  80% { transform: translateX(3px) scale(1.01); }
  100% { transform: translateX(0) scale(1); }
}

</style>
