<template>
  <div class="container">
    <div class="share-text">
  <h3>お疲れさま 共有しよう！</h3>
  <a :href="blogPostUrl" class="link">投稿</a>
</div>


    <div class="timer-select card">
      <p class="card-title">運動はあと何分後に再開しますか？<br>
        待機時間完了後にガチャをもう一度引けます
      </p>
      <label for="duration">待機時間を選択:</label>
      <select id="duration" v-model="selectedDuration" class="select-box">
        <option v-for="min in [5,10,20,25,30]" :key="min" :value="min">
          {{ min }} 分
        </option>
      </select>
    </div>

    <div class="button-group">
      <button @click="startTimer" :disabled="timerStarted" class="button primary">
        タイマー開始
      </button>
      <button @click="goHome" class="button secondary">トップへ戻る</button>
    </div>

    <p v-if="timerStarted" class="remaining-time">残り時間: {{ remainingTime }} 秒</p>
    <p v-else class="remaining-time">タイマーは開始されていません</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const blogPostUrl = ref('http://127.0.0.1:8000/blog/post/new/')
const timerStarted = ref(false)
const remainingTime = ref(0)
const selectedDuration = ref(10) // デフォルト10分
let timerInterval = null

const VAPID_PUBLIC_KEY =
  'BGDYJ1cA4_I3UbukEqt8SHMnWTSXqE06B6HAk78XZMh_I3W8ziWvM3jpq1VVvonGcSvjNmVskVvFhyxOeNolqng'

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const rawData = window.atob(base64)
  return Uint8Array.from([...rawData].map((char) => char.charCodeAt(0)))
}

// Django CSRF トークン取得
function getCSRFToken() {
  const name = 'csrftoken'
  const cookieValue = document.cookie
    .split('; ')
    .find(row => row.startsWith(name + '='))
  return cookieValue ? decodeURIComponent(cookieValue.split('=')[1]) : ''
}

const startTimer = async () => {
  try {
    const registration = await navigator.serviceWorker.ready

    const existingSubscription = await registration.pushManager.getSubscription()
    if (existingSubscription) {
      await existingSubscription.unsubscribe()
      console.log('古いPush購読を解除しました')
    }

    const subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY),
    })

    // 選択した分数をそのまま送信
    const duration_minutes = selectedDuration.value

    await axios.post(
      'http://127.0.0.1:8000/timer/api/start-timer/',
      {
        subscription_info: subscription.toJSON(),
        duration: duration_minutes, // サーバーで request.data.get('duration') で取得
      },
      {
        withCredentials: true,
        headers: { 'X-CSRFToken': getCSRFToken() },
      }
    )

    startLocalTimer(duration_minutes * 60) // フロント用カウントダウン（秒換算）
  } catch (err) {
    console.error(err)
    alert('タイマー開始に失敗しました')
  }
}

// フロントでカウントダウンを表示する場合のみ使用
const startLocalTimer = (seconds) => {
  timerStarted.value = true
  remainingTime.value = seconds

  clearInterval(timerInterval)
  timerInterval = setInterval(() => {
    remainingTime.value--
    if (remainingTime.value <= 0) {
      clearInterval(timerInterval)
      timerStarted.value = false
      alert('タイマー終了！')
    }
  }, 1000)
}

const fetchTimerStatus = async () => {
  try {
    const res = await axios.get(
      'http://127.0.0.1:8000/timer/api/current-timer/',
      { withCredentials: true }
    )
    const { end_time } = res.data
    if (end_time) {
      const remaining = Math.floor((new Date(end_time).getTime() - Date.now()) / 1000)
      if (remaining > 0) startLocalTimer(remaining)
    }
  } catch (err) {
    console.error('タイマー状態取得に失敗:', err)
  }
}

const goHome = () => {
  window.location.href = 'http://127.0.0.1:8000/'
}

onMounted(() => {
  fetchTimerStatus()
})
</script>

<style scoped>
/* =======================
  コンテナ & カード
======================= */
.container {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: center;
  padding: 30px;
  max-width: 450px;
  margin: 50px auto;
  background: #ffffff;
  border-radius: 15px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.1);
}

.card {
  width: 100%;
  background: #f9f9f9;
  border-radius: 15px;
  padding: 20px 25px;
  margin-bottom: 20px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.card-title {
  font-size: 1.2em;
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
  text-align: center;
}

/* =======================
  タイポグラフィ & リンク
======================= */
.share-text {
  text-align: center;
  margin-bottom: 25px;
}

.share-text h3 {
  font-size: 1.5em;       /* 適度に大きく */
  font-weight: 600;
  color: #4CAF50;         /* 背景と区別できる色 */
  margin: 6px 0 12px 0;   /* 上下の余白を調整 */
  line-height: 1.4;       /* 行間を微調整 */
  word-break: break-word;  /* 長い文章を折り返す */
}



.link {
  color: #2196F3;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s;
}

.link:hover {
  color: #0b7dda;
  text-decoration: underline;
}


/* =======================
  ボタン
======================= */
.button-group {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.button {
  padding: 12px 28px;
  border: none;
  border-radius: 25px;
  font-size: 1em;
  font-weight: 500;
  color: #fff;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.button.primary {
  background: linear-gradient(135deg, #4CAF50, #66BB6A);
  box-shadow: 0 6px 15px rgba(76,175,80,0.3);
}

.button.primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(76,175,80,0.4);
}

.button.secondary {
  background: linear-gradient(135deg, #2196F3, #42A5F5);
  box-shadow: 0 6px 15px rgba(33,150,243,0.3);
}

.button.secondary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(33,150,243,0.4);
}

/* =======================
  セレクトボックス
======================= */
.select-box {
  padding: 10px 14px;
  border-radius: 12px;
  border: 1px solid #ddd;
  background-color: #ffffff;
  font-size: 1em;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.select-box:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 5px rgba(76,175,80,0.4);
}

/* =======================
  タイマー表示
======================= */
.remaining-time {
  font-size: 1.3em;
  color: #FF5722;
  font-weight: 600;
  margin-top: 12px;
  animation: fadeIn 0.4s ease;
}

@keyframes fadeIn {
  0% { opacity: 0; transform: translateY(10px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>