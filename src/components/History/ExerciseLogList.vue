<script setup>
import { ref, onMounted, computed } from 'vue'
import { 
  format, eachDayOfInterval, subDays, 
  getDay, isSameDay 
} from 'date-fns'
import { useExerciseStore } from '../../stores/useExerciseStore'
import html2canvas from 'html2canvas'
import StampCard from '../../components/StampCard.vue'

const store = useExerciseStore() // Storeの使用準備
const selectedDay = ref(null)

// カレンダー生成: 過去31日分のデータを生成
const calendarDays = computed(() => {
  const today = new Date()
  // 過去30日前から今日までの31日間を取得
  const start = subDays(today, 30)
  const days = eachDayOfInterval({ start, end: today })
  
  return days.map(date => {
    const dateStr = format(date, 'yyyy-MM-dd')
    // store.stamps から合致する日付を検索
    const dayData = store.stamps.find(s => s.date === dateStr)

    return {
      dateObj: date,
      dayNum: format(date, 'd'),
      monthStr: format(date, 'M'),
      dayOfWeek: getDay(date),
      isToday: isSameDay(date, today),
      data: dayData
    }
  })
})

// クリックした時の処理
const openDetail = (day) => {
  if (day?.data) {
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

// シェア機能のロジック
const shareDailyResult = async () => {
  const element = document.getElementById('daily-share-area');
  if (!element) return;

  try {
    const canvas = await html2canvas(element, {
      backgroundColor: '#ffffff',
      ignoreElements: (el) => 
        el.classList.contains('share-daily-btn') || 
        el.classList.contains('close-btn')
    });

    canvas.toBlob(async (blob) => {
      const file = new File([blob], `exercise-${selectedDay.value.date}.png`, { type: 'image/png' });
      
      if (navigator.share) {
        await navigator.share({
          files: [file],
          title: '今日の運動記録',
          text: `${selectedDay.value.date} はこれだけ運動しました！ #FitSpin`
        });
      } else {
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `FitSpin-${selectedDay.value.date}.png`;
        link.click();
      }
    });
  } catch (err) {
    console.error('Share failed:', err);
  }
};

onMounted(() => {
  store.initialize()
})
</script>

<template>
  <div class="gacha-container">
    <div class="storage-container">

      <h1 class="main-title">運動の記録</h1>

      <div class="calendar-card">
        <div class="calendar-grid">
          <div 
            v-for="(day, index) in calendarDays" 
            :key="index"
            @click="openDetail(day)" 
            :class="{ 
              'is-today': day?.isToday,
              'clickable': day?.data
            }"
            class="calendar-cell"
          >
            <span class="date-num">{{ day.monthStr }}/{{ day.dayNum }}</span>
            
            <div v-if="day?.data" class="mini-sticker">
              <span class="sticker-icon">{{ day.data.symbol }}</span>
            </div>
          </div>
        </div>
      </div>

      <Transition name="fade">
        <div v-if="selectedDay" class="modal-overlay" @click="selectedDay = null">
          <div class="detail-card" id="daily-share-area" @click.stop>
            <h3 class="detail-date">{{ selectedDay.date }} の全記録</h3>
            
            <div class="log-list">
              <div v-for="(log, idx) in selectedDay.logs" :key="idx" class="log-item">
                <span class="log-time">{{ log.time }}</span>
                <span class="log-symbol">Lv.{{ log.level }} {{ log.symbol || '✨' }}</span>
                <span class="log-text">{{ log.text }}</span>
              </div>
            </div>

            <div class="result-actions">
              <button @click="shareDailyResult" class="share-daily-btn">
                📱 今日のまとめをシェア
              </button>
              
              <button class="close-btn" @click="selectedDay = null">とじる</button>
            </div>
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
.gacha-container { width: 100%; min-height: 100vh; background-color: #FFFDE7; display: flex; flex-direction: column; align-items: center; }
.storage-container { padding: 20px; width: 100%; max-width: 600px; }
.main-title { font-size: 28px; text-align: center; margin-bottom: 30px; font-weight: 900; color: #2D3436; }

.calendar-card { 
  background: white; 
  /* カレンダー全体を囲む枠線をくすんだオレンジに変更し、シャドウも同色に */
  border: 4px solid #E67E22; 
  border-radius: 20px; 
  padding: 20px; 
  box-shadow: 8px 8px 0px #E67E22; 
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 6px;
}

.calendar-cell {
  height: 65px;
  border: 2px solid #2D3436;
  border-radius: 8px;
  background: #FAFAFA;
  padding: 4px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  cursor: default;
}

.is-today { 
  background-color: #FFF9C4; 
  /* 今日のみ枠線を「くすんだ緑」にして強調 */
  border: 3px solid #00B894 !important; 
}

.date-num { 
  font-size: 10px; 
  font-weight: 900; 
  color: #2D3436; 
}
.mini-sticker { 
  font-size: 20px; 
  pointer-events: none;
}

.footer-nav { margin-top: 40px; text-align: center; }
.back-link-bottom { text-decoration: none; color: #6C5CE7; font-weight: bold; }

.clickable { cursor: pointer; transition: background 0.2s; }
.clickable:hover { filter: brightness(0.95); }

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

.result-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  margin-top: 20px;
}

.share-daily-btn, .close-btn {
  padding: 10px 14px;
  border-radius: 12px;
  border: 3px solid #2D3436;
  font-weight: 900;
  cursor: pointer;
  transition: all 0.1s;
  font-size: 13px;
  outline: none;
}

.share-daily-btn {
  background: #6C5CE7;
  color: white;
  box-shadow: 3px 3px 0px #2D3436;
}

.close-btn {
  background: #2D3436;
  color: white;
  box-shadow: 3px 3px 0px rgba(0,0,0,0.2);
}

.share-daily-btn:active, .close-btn:active {
  transform: translate(2px, 2px);
  box-shadow: 0px 0px 0px #2D3436;
}

.share-daily-btn:hover { filter: brightness(1.1); }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>