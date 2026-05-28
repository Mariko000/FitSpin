<script setup>
import { ref, onMounted, computed } from 'vue'
import { 
  format, startOfMonth, endOfMonth, eachDayOfInterval, 
  getDay, isSameDay 
} from 'date-fns'


const stamps = ref([])
const today = new Date() // 常に「今日」を基準にする
// クリックされた日のデータを保持する変数
const selectedDay = ref(null)

// カレンダー生成（常に今月のみ）
const calendarDays = computed(() => {
  const start = startOfMonth(today)
  const end = endOfMonth(today)
  const daysInMonth = eachDayOfInterval({ start, end })
  const startDay = getDay(start)
  const padding = Array(startDay).fill(null)

  return [
    ...padding,
    ...daysInMonth.map(date => {
      const dateStr = format(date, 'yyyy-MM-dd')
      // 保存データ(31日分)の中から、カレンダーの日付に合うものを探す
      const dayData = stamps.value.find(s => s.date === dateStr)

      return {
        dayNum: format(date, 'd'),
        dayOfWeek: getDay(date),
        isToday: isSameDay(date, today),
        data: dayData
      }
    })
  ]
})
// クリックした時の処理
const openDetail = (day) => {
  console.log("クリックされた日:", day); // ブラウザのコンソールでデータを確認できます
  
  if (day?.data) {
    // もし古いデータで logs がない場合は、空の配列を作ってあげる
    if (!day.data.logs) {
      day.data.logs = [{
        time: "--:--",
        symbol: day.data.symbol,
        text: "（この日の詳細は記録されていません）",
        level: day.data.level
      }];
    }
    selectedDay.value = day.data;
  }
}

onMounted(() => {
  // 保存されている全データ（最大31日分）を読み込む
  stamps.value = JSON.parse(localStorage.getItem('stampHistory') || '[]')
})
</script>

<template>
  <div class="gacha-container">
    <div class="storage-container">
      <h1 class="main-title">{{ format(today, 'yyyy年 M月') }}の記録</h1>

      <div class="calendar-card">
        <table class="calendar-table">
          <thead>
            <tr>
              <th class="sun">日</th><th>月</th><th>火</th><th>水</th><th>木</th><th>金</th><th class="sat">土</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(week, i) in Math.ceil(calendarDays.length / 7)" :key="i">
              <td v-for="(day, j) in calendarDays.slice(i * 7, (i + 1) * 7)" :key="j"
                  @click="openDetail(day)" 
                  :class="{ 
                    'sun-bg': day?.dayOfWeek === 0, 
                    'sat-bg': day?.dayOfWeek === 6,
                    'is-today': day?.isToday,
                    'clickable': day?.data // データがある日はクリックできる印
                  }">
                <span v-if="day" class="date-num">{{ day.dayNum }}</span>
                
                <div v-if="day?.data" class="mini-sticker">
                  <span class="sticker-icon">{{ day.data.symbol }}</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- ★ここから追加：詳細表示エリア（モーダル） -->
      <Transition name="fade">
        <div v-if="selectedDay" class="modal-overlay" @click="selectedDay = null">
          <div class="detail-card" @click.stop>
            <h3 class="detail-date">{{ selectedDay.date }} の全記録</h3>
            <div class="log-list">
              <div v-for="(log, idx) in selectedDay.logs" :key="idx" class="log-item">
                <span class="log-time">{{ log.time }}</span>
                <span class="log-symbol">Lv.{{ log.level }} {{ log.symbol || '✨' }}</span>
                <span class="log-text">{{ log.text }}</span>
              </div>
            </div>
            <button class="close-btn" @click="selectedDay = null">とじる</button>
          </div>
        </div>
      </Transition>

      <div class="footer-nav">
        <router-link to="/exercise-done" class="back-link-bottom">← 管理画面に戻る</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 基本スタイルは以前の「ポップ＆クール」なデザインを継承 */
.gacha-container { width: 100%; min-height: 100vh; background-color: #FFFDE7; display: flex; flex-direction: column; align-items: center; }
.storage-container { padding: 20px; width: 100%; max-width: 600px; }
.main-title { font-size: 28px; text-align: center; margin-bottom: 30px; font-weight: 900; color: #2D3436; }

.calendar-card { background: white; border: 4px solid #2D3436; border-radius: 20px; padding: 15px; box-shadow: 8px 8px 0px #2D3436; }
.calendar-table { width: 100%; border-collapse: collapse; table-layout: fixed; }
.calendar-table th { background: #4A86E8; color: white; padding: 10px 0; border: 2px solid #2D3436; }
.calendar-table td { height: 80px; border: 1px solid #dfe6e9; vertical-align: top; padding: 5px; }

.sun-bg { background-color: #FADBD8; }
.sat-bg { background-color: #D1F2EB; }
.is-today { background-color: #FFF9C4; border: 2px solid #2D3436 !important; }

.date-num { font-size: 12px; font-weight: bold; color: #636e72; }
.mini-sticker { text-align: center; font-size: 28px; margin-top: 5px; }

.footer-nav { margin-top: 40px; text-align: center; }
.back-link-bottom { text-decoration: none; color: #6C5CE7; font-weight: bold; }

/* ★追加：クリック可能なマスのカーソル */
.clickable { cursor: pointer; transition: background 0.2s; }
.clickable:hover { filter: brightness(0.95); }

/* ★追加：詳細画面（モーダル）のスタイル */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.7); display: flex; justify-content: center; align-items: center; z-index: 1000;
  backdrop-filter: blur(4px);
}
.detail-card {
  background: white; width: 90%; max-width: 400px; padding: 25px; border-radius: 20px;
  border: 4px solid #2D3436; box-shadow: 10px 10px 0px #2D3436;
}
.detail-date { margin-top: 0; border-bottom: 3px solid #6C5CE7; padding-bottom: 10px; font-weight: 900; }

.log-list { margin: 20px 0; max-height: 300px; overflow-y: auto; }
.log-item {
  display: flex; align-items: center; gap: 10px; padding: 12px 0;
  border-bottom: 2px dashed #dfe6e9;
}
.log-time { font-size: 11px; color: #636e72; width: 60px; }
.log-symbol { font-size: 18px; }
.log-text { font-weight: bold; color: #2D3436; flex: 1; }

.close-btn {
  width: 100%; padding: 12px; background: #2D3436; color: white;
  border: none; border-radius: 12px; font-weight: 900; cursor: pointer;
}

/* アニメーション */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* mini-stickerの中の絵文字がクリックを邪魔しないようにする */
.mini-sticker {
  pointer-events: none; /* これで絵文字を突き抜けて下の td がクリックされるようになります */
}
</style>