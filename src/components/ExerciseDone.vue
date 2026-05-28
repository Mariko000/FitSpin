<script setup>
// --- script部分は変更なし ---
import { ref, onMounted } from 'vue'
import StampCard from '@/components/StampCard.vue'
import { useExerciseStore } from '../stores/useExerciseStore' // Storeをインポート

// --- Storeのセットアップ ---
const store = useExerciseStore() //

// マイスタンプ帳のモーダル表示フラグ
const showStampCard = ref(false)

const stamps = ref([])
const dailyCount = ref(0)
const lastSpinDate = ref('')

const loadAllData = () => {
  stamps.value = JSON.parse(localStorage.getItem('stampHistory') || '[]')
  dailyCount.value = localStorage.getItem('dailyCount') || 0
  lastSpinDate.value = localStorage.getItem('lastSpinDate') || '未記録'
}

// データの初期化ボタンの動作はそのまま維持
const resetEverything = () => {
  if (confirm('すべてのデータ（履歴・カウント・日付）を完全に削除しますか？')) {
    localStorage.removeItem('stampHistory')
    localStorage.removeItem('dailyCount')
    localStorage.removeItem('lastSpinDate')
    loadAllData() 
    alert('すべてのデータを削除しました。')
  }
}

onMounted(loadAllData)
</script>

<template>
  <div class="gacha-container data-management-page">
    <div class="storage-container">
      <div class="header-row">
        <h2>データ管理</h2>
      </div>

      <section class="status-section">
        <h3>今日の運動履歴</h3>
        <div class="status-card sticker-style">
          <p>最終実施日: <span>{{ lastSpinDate }}</span></p>
          <p>本日のカウント: <span class="count-text">{{ dailyCount }} / 3</span></p>
        </div>
      </section>

      <section class="history-section nav-group">
        <h3>運動の記録</h3>
        <router-link to="/exercise-logs" class="log-list-link sticker-btn-green">
          過去31日分の記録 →
        </router-link>
      </section>

      <div class="actions-header" style="margin-top: 20px; text-align: center; margin-bottom: 30px;">
        <button @click="showStampCard = true" class="open-stamp-btn">
          マイ スタンプ帳を見る
        </button>
      </div>

      <Transition name="fade">
        <div v-if="showStampCard" class="modal-overlay" @click="showStampCard = false">
          <div class="stamp-card-wrapper" @click.stop>
            <StampCard />
            <button @click="showStampCard = false" class="close-btn">とじる</button>
          </div>
        </div>
      </Transition>

      <section class="danger-zone isolation-group">
        <button @click="resetEverything" class="reset-btn small-danger-btn">
          全データの初期化
        </button>
      </section>



      <div class="footer-nav">
        <router-link to="/" class="back-link">← 戻る</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* --- 全体のレイアウト設定 --- */
.data-management-page {
  display: flex;
  flex-direction: column;
  align-items: center; /* 中身を中央へ */
  padding-bottom: 40px; /* 下部に余白 */
}

.storage-container {
  padding: 20px;
  width: 100%;
  max-width: 420px; /* おばあちゃんが見やすい幅に制限 */
  color: #2D3436;
}

.header-row {
  text-align: center;
  margin-bottom: 40px;
}

h3 {
  font-size: 16px;
  color: #636e72;
  margin-bottom: 12px;
}

/* --- [テーマ：ステッカー感] 今日の運動履歴カード --- */
.sticker-style {
  background: white;
  border: 4px solid #2D3436; /* 枠線を太く */
  padding: 20px;
  border-radius: 18px; /* 丸みを強く */
  /* [ステッカー感] ベタ塗りの影を大きく、少し斜めに */
  box-shadow: 8px 8px 0px #2D3436; 
  margin-bottom: 30px;
}

.status-card p {
  font-size: 16px;
  margin-bottom: 8px;
  font-weight: bold;
}

.count-text {
  font-size: 20px;
  font-weight: 900;
  color: #6C5CE7; /* 紫色で強調 */
}

/* --- [テーマ：ステッカー感] 7日間の記録を見る ボタン --- */
.nav-group {
  margin-bottom: 60px; /* 下の初期化ボタンと大きく距離を離す */
}

.log-list-link {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 55px; /* 今の大きさを維持 */
  font-size: 18px;
  font-weight: 900;
  color: white;
  text-decoration: none;
  border-radius: 15px;
  /* [修正] 色をLv.2のグリーンに */
  background: #4ECDC4; 
  border: 4px solid #2D3436;
  /* [ステッカー感] 大きめの影 */
  box-shadow: 6px 6px 0px #2D3436; 
  transition: all 0.1s;
}

/* クリックした時の沈むアニメーション */
.log-list-link:active {
  transform: translate(3px, 3px);
  box-shadow: 2px 2px 0px #2D3436;
}

/* --- [テーマ：小さく離す] 全データの初期化 ボタン --- */
.isolation-group {
  margin-top: auto; /* 可能なら下に張り付かせる */
  text-align: center;
  border-top: 2px dashed #dfe6e9; /* 区切り線を入れて別エリアだと強調 */
  padding-top: 20px;
}

.small-danger-btn {
  background: #ff7675; /* 元の赤色を維持 */
  color: white;
  border: 3px solid #2D3436;
  /* [修正] 一回り小さく */
  padding: 8px 20px;
  font-size: 13px;
  font-weight: bold;
  border-radius: 10px;
  cursor: pointer;
  box-shadow: 3px 3px 0px #2D3436;
  width: auto; /* 幅を自動にして小さく見せる */
  display: inline-block;
}

.small-danger-btn:active {
  transform: translate(2px, 2px);
  box-shadow: 1px 1px 0px #2D3436;
}

.open-stamp-btn {
  background: #FFD93D; color: #2D3436; font-weight: 900; padding: 12px 24px;
  border: 3px solid #2D3436; border-radius: 15px; cursor: pointer;
  box-shadow: 4px 4px 0px #2D3436; transition: all 0.1s;
}
.open-stamp-btn:hover {
  filter: brightness(1.1);
}
.open-stamp-btn:active {
  transform: translate(2px, 2px);
  box-shadow: 0px 0px 0px #2D3436;
}

/* モーダル共通スタイル（必要に応じてデータ管理画面に追加） */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.7); display: flex; justify-content: center; align-items: center; z-index: 1000;
  backdrop-filter: blur(4px);
}
.stamp-card-wrapper {
  display: flex; flex-direction: column; align-items: center; gap: 15px;
  width: 90%; max-width: 400px;
}
.close-btn {
  padding: 10px 20px; border-radius: 15px; border: 3px solid #2D3436;
  font-weight: 900; cursor: pointer; width: 100%; background: #2D3436; color: white;
  box-shadow: 4px 4px 0px rgba(0, 0, 0, 0.2);
}
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* --- 戻るリンク（一番下） --- */
.footer-nav {
  margin-top: 50px;
  display: flex;
  justify-content: center;
}

.back-link {
  text-decoration: none;
  color: #6C5CE7;
  font-weight: bold;
  font-size: 14px;
  padding: 10px;
}
</style>