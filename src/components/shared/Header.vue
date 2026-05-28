<script setup>
import { ref, onMounted, computed } from 'vue'
import { useExerciseStore } from '../../stores/useExerciseStore'

// ★ 追加：Storeの呼び出しをテンプレートとスクリプトから読めるように定義
const store = useExerciseStore()

// メニューの開閉状態を管理する
const isMenuOpen = ref(false)

const streakCount = ref(0)
const dailyCount = ref(0) // 今日の回数

// スライダーの開閉フラグ
const showSlider = ref(false)

onMounted(() => {
  const updateRates = () => {
    const savedStreak = parseInt(localStorage.getItem('streakCount') || '0')
    const savedDaily = parseInt(localStorage.getItem('dailyCount') || '0') // 今日何回回したかも取得
    streakCount.value = savedStreak
    dailyCount.value = savedDaily // dailyCountをrefで定義しておく必要あり
  }

  updateRates()

  // 他のコンポーネントでlocalStorageが更新されたのを検知する
  window.addEventListener('storage', updateRates)
  
  // Custom Event（同じタブ内での更新検知用）
  window.addEventListener('spin-updated', updateRates)
})

// MainContentと同じロジックを置く

const updateProgress = (result) => {
  const today = new Date().toISOString().split('T')[0]
  
  // 1. カウントアップ
  dailyCount.value += 1
  localStorage.setItem('dailyCount', dailyCount.value.toString())
  // ★ 追加：ヘッダーに「更新したよ！」と叫ぶ
  window.dispatchEvent(new Event('spin-updated'))
  
  const savedStamps = JSON.parse(localStorage.getItem('stampHistory') || '[]')
  let todayStamp = savedStamps.find(s => s.date === today)

  if (!todayStamp) {
    // 1回目の時：新しいスタンプデータを作成
    todayStamp = {
      date: today,
      symbol: symbols[result.level - 1],
      count: dailyCount.value, // ここで1〜3を管理
      hasBadge: false
    }
    savedStamps.push(todayStamp)
  } else {
    // 2回目以降：カウントのみ更新
    todayStamp.count = dailyCount.value
    if (dailyCount.value >= 3) todayStamp.hasBadge = true
  }

  // 7日分を維持して保存
  const updated = savedStamps.slice(-7)
  stamps.value = updated
  localStorage.setItem('stampHistory', JSON.stringify(updated))
  localStorage.setItem('lastSpinDate', today)

  // ★ ここで定義済みの saveBadge をしっかり使う！
  if (dailyCount.value >= 3) {
    saveBadge(today)
  }
}

const currentRareRate = computed(() => {
  // 1. ベースの確率 (0.2 = 20%)
  const baseRate = 0.2; 

  // 2. 継続日数ボーナス (1日につき 5%)
  const streakBonus = streakCount.value * 0.05;

  // 3. ★ここ！「今日回した回数」による加算 (1回につき 10%)
  // 「2回目で30%」にするなら、1回スピンした後の effortBonus が 0.10 になればOK
  const effortBonus = dailyCount.value * 0.10; 
  
  return Math.min(baseRate + streakBonus + effortBonus, 0.8); 
})

// ★ ここに「高レベル出現UP中！」の出し分けロジック
const rateStatus = computed(() => {
  const rate = currentRareRate.value;

  if (rate >= 0.7) {
    return {
      text: '激レアチャンス！',
      color: '#FF00FF'
    };
  }

  if (rate >= 0.5) {
    return {
      text: '高レベル出現UP中！',
      color: '#FF6B6B'
    };
  }

  if (rate >= 0.3) {
    return {
      text: 'Lv3確率上昇中',
      color: '#6C5CE7'
    };
  }

  return {
    text: '通常モード',
    color: '#2D3436'
  };
});

// 通知許可を求める関数
const enableGhostNotification = async () => {
  const permission = await Notification.requestPermission();
  if (permission === 'granted') {
    alert('お化けがあなたの後ろに並びました...');
    sendNotificationTaskToSW();
  }
};

// Service Workerに「1時間後に通知」を命令する実体
const sendNotificationTaskToSW = async () => {
  if ('serviceWorker' in navigator) {
    const registration = await navigator.serviceWorker.ready;
    if (registration.active) {
      registration.active.postMessage({
        type: 'SCHEDULE_GHOST'
      });
      console.log('お化けのタイマーをセットしました（Ready経由）');
    } else {
      console.warn('Service Workerの実体が見つかりません');
    }
  } else {
    console.warn('このブラウザはService Worker非対応です');
  }
};


</script>

<template>
  <nav class="custom-navbar">
    <div class="custom-container">

      <!-- ロゴ -->
      <div class="logo-wrapper" :class="{ 'is-open': isMenuOpen }">
        <router-link to="/">
          <img src="@/assets/logo/Top_name.PNG" alt="FitSpin" class="logo-img" />
        </router-link>
      </div>

      <!-- ハンバーガーボタン -->
      <button class="hamburger-btn" @click="isMenuOpen = !isMenuOpen">
        <i class="fa-solid" :class="isMenuOpen ? 'fa-xmark' : 'fa-bars'"></i>
      </button>

      <!-- 右側メニュー -->
      <div
        class="header-right-group"
        :class="{ 'is-open': isMenuOpen }"
      >
      <!-- <div style="color:red;">TEST</div> -->

        <div class="audio-controller-header">
          <label class="audio-toggle-header" :title="store.isMuted ? 'サウンドON' : 'サウンドOFF'">
            <input type="checkbox" v-model="store.isMuted" />
            <span class="toggle-btn-header">
              <i v-if="store.isMuted" class="fa-solid fa-toggle-off"></i>
              <i v-else class="fa-solid fa-toggle-on"></i>
            </span>
          </label>

          <button 
            class="slider-toggle-btn" 
            @click="showSlider = !showSlider" 
            title="音量調節"
          >
            <i class="fa-solid fa-sliders"></i>
          </button>

          <input 
            v-if="showSlider"
            type="range" 
            min="0" 
            max="1" 
            step="0.05" 
            :value="store.volume"
            @input="store.volume = parseFloat($event.target.value)"
            class="volume-slider-header" 
            :disabled="store.isMuted"
            :style="{ opacity: store.isMuted ? '0.5' : '1' }"
          />
        </div>

        <div class="rate-status" :style="{ color: rateStatus.color }">
          {{ rateStatus.text }}
          <span class="rate-num">({{ (currentRareRate * 100).toFixed(0) }}%)</span>
        </div>

         <!-- スタンプコレクション -->
        <router-link to="/StampCollection" class="nav-icon-link">
          <i class="fa-solid fa-crown"></i>
        </router-link>

 <!-- 通知ボタン -->
<button @click="enableGhostNotification" class="notif-button">
  <i class="fa-solid fa-bell"></i>
</button>

<!-- 設定リンク -->
<router-link to="/exercise-done" class="settings-link">
  <i class="fa-solid fa-gear"></i>
</router-link>
        
      </div>
    </div>
  </nav>
</template>

<style>
.custom-navbar {
  position: relative;
  z-index: 1000;
  background-color: #FFFDE7;
  height: 40px; 
}

.custom-container {
  position: relative;
  width: 100%;
  height: 100%;
  
  /* Flexboxは使うけど、中身を「右詰め」にする */
  display: flex;
  justify-content: flex-end; /* ここをspace-betweenから変更 */
  align-items: center;
  
  padding: 0 15px; /* 右端の⚙️アイコンの余白 */
}

/* ステータス表示のスタイル */
.rate-status {
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.05em;
  text-align: right;
  line-height: 1.2;
}

.rate-num {
  font-size: 9px;
  opacity: 0.7;
  margin-left: 4px;
}

.logo-img {
  height: 420px; 
  width: auto;
  position: absolute;
  top: -155px; 
  left: -20px; 
  z-index: 1001;
  pointer-events: auto; 
  cursor: pointer; /* マウスを乗せた時に指マークにする */
}

.header-right-group {
  position: absolute; /* 親(container)に対して自由に動かせるようにする */
  
  /* ⚙️アイコンが来る位置を右端からの距離で指定 */
  /* オレンジ枠の位置に合わせて 100px〜150px くらいで調整してください */
  right: 120px; 
  
  top: 50%;
  transform: translateY(-50%); /* 縦方向の中央揃え */
  
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 1002;
}

/* サウンドコントロールのスタイル */
.audio-controller-header {
  display: flex;
  align-items: center;
  gap: 10px;
  background: transparent;
  padding: 0;
  border: none;
  box-shadow: none;
}

.audio-toggle-header input {
  display: none;
}

.toggle-btn-header {
  cursor: pointer;
  font-size: 20px;
  color: #656565;
  display: flex;
  align-items: center;
  transition: transform 0.1s;
}

.toggle-btn-header:active {
  transform: scale(0.9);
}

.slider-toggle-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  font-size: 20px;
  color: #2D3436;
  display: flex;
  align-items: center;
  transition: transform 0.1s;
}

.slider-toggle-btn:active {
  transform: scale(0.9);
}

.volume-slider-header {
  width: 60px;
  cursor: pointer;
  accent-color: #575758;
  vertical-align: middle;
  margin-left: 2px;
}
/* クラウン、ベル、歯車の共通設定 */
.nav-icon-link, 
.notif-button, 
.settings-link {
  text-decoration: none;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  
  /* 色とサイズを完全に統一 */
  color: #95a5a6; 
  font-size: 28px; 
  
  transition: transform 0.3s ease, color 0.3s ease;
}

/* クラウン特有のホバー演出（以前の紫指定を解除） */
.nav-icon-link:hover {
  transform: scale(1.1);
  color: #7f8c8d; /* 少し濃いグレーに */
}

/* 通知ボタンのホバー演出 */
.notif-button:hover {
  transform: scale(1.1);
  color: #7f8c8d;
}

/* クリック時に少し縮むエフェクト */
.notif-button:active {
  transform: scale(0.95); 
}

/* 設定リンク（歯車アイコン） */
.settings-link {
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #95a5a6; /* グレー色 */
  font-size: 28px;
  transition: transform 0.3s ease;
}

/* ホバー時に歯車を回転させる演出 */
.settings-link:hover {
  transform: rotate(45deg);
}
/* PCではハンバーガー隠す */
.hamburger-btn {
  display: none;
}
@media (max-width: 600px) {

/* ロゴ縮小 */
.logo-img {
  height: 180px;
  top: -60px;
  left: -10px;
}

/* ハンバーガー表示 */
.hamburger-btn {
  display: block;
  position: fixed;
  top: 10px;
  right: 15px;
  z-index: 1201;

  background: none;
  border: none;
  font-size: 28px;
  color: #2D3436;
  cursor: pointer;
}

/* 通常時は非表示 */
.header-right-group {
  display: none;

  opacity: 0;
  visibility: hidden;

  position: fixed;
  top: 0;
  left: 0;

  width: 100vw;
  height: 100vh;

  background: #FFFDE7;
  z-index: 1200;

  transition:
    opacity 0.25s ease,
    visibility 0.25s ease;
}

/* 開いた時だけ表示 */
.header-right-group.is-open {
  display: flex !important;
  opacity: 1;
  visibility: visible;

  flex-direction: column;
  align-items: center;
  justify-content: flex-start;

  padding-top: 100px;
  gap: 24px;

  right: auto !important;
  top: 0 !important;
  transform: none !important;

  background: rgba(255, 253, 231, 0.88);

  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}


/* メニュー内 */
.audio-controller-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
}

.rate-status {
  text-align: center;
}

.nav-icon-link,
.notif-button,
.settings-link {
  font-size: 32px;
}
}


/* 
数値の変化スケジュール
1回も回していない時：

dailyCount が 0 なので、20%（＋継続ボーナス）

表示： 通常モード (20%)

1回回した後：

dailyCount が 1 になり、30%（＋継続ボーナス）

表示： 確率上昇中 (30%)

2回回した後：

dailyCount が 2 になり、40%（＋継続ボーナス）

表示： 確率上昇中 (40%) */
</style>