<script setup>
import { ref, onMounted, computed } from 'vue'
import { exerciseLevels } from '../exercise/exercise_levels.js'

import circleSmall from '../assets/images/badges/cell-circle_small.png'
import circleMedium from '../assets/images/badges/cell-circle_medium.png'
import circleLarge from '../assets/images/badges/cell-circle_large.png'

// 効果音のインポート
import spinSePath from '../assets/sounds/spin.mp3'
import winSePath from '../assets/sounds/win.mp3'

// 今日のトレーニングをシェア
import html2canvas from 'html2canvas';

// --- キャラクター管理 ---
// 状態: 'idle'(待機), 'moving'(左から移動中), 'jumping'(ジャンプ中),'climbing' 'finished'(腰掛け完了)
const charState = ref('idle');
const isClicked = ref(false); // ★ 追加：クリックされたかどうかのフラグ
let ghostTimer = null; // タイマー保持用

const rotation = ref(0)
const spinning = ref(false)
const exerciseResult = ref(null)

const symbols = ['✨', '⭐', '😊', '🕶️', '🌈']; // レベル1〜5に対応

// 抽選のタイミング: spin を押した瞬間に、裏側で「Lv.1の〇〇」という結果は決まっています。
// ルーレットの停止位置: 決まった level に基づいて、ルーレットの角度を計算して止めます。
// 結果の表示: await を使って、ルーレットがピタッと止まるまで exerciseResult.value を更新しないようにしています。

const showStampCard = ref(false);
const stamps = ref([]) // 履歴
const dailyCount = ref(0) // 今日の回数
const streakCount = ref(0)// 連続ログイン数
const hasStampingToday = ref(false) // 今日スタンプ済みか
const hasBadgeToday = ref(false) // 今日バッジ獲得済みか

// --- Audio Objects ---
const spinSe = new Audio(spinSePath)
const winSe = new Audio(winSePath)

// 要素を等間隔に配置する計算
const getSectorStyle = (index) => {
  const totalSectors = 5
  const angle = 360 / totalSectors
  // rotateで向きを決め、translateYで円周上に飛ばし、再度rotateで文字の向きを直す
  return {
    transform: `
      rotate(${angle * index}deg) 
      translateY(-110px) 
      rotate(${-angle * index}deg)
    `
  }
}

// プログレスバーのスタイル計算
const progressBarStyle = computed(() => {
  const max = 3;
  const radius = 180; // このサイズを基準にします
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (Math.min(dailyCount.value, max) / max) * circumference;
  return {
    strokeDasharray: circumference,
    strokeDashoffset: offset,
    transition: 'stroke-dashoffset 0.8s ease-in-out'
  };
});

// 結果を閉じてスタンプカードを表示する
const confirmResult = () => {
  exerciseResult.value = null; // 結果画面を閉じる
  showStampCard.value = true;  // スタンプカードを表示する
};

// スタンプカードを閉じてルーレットに戻る
const closeStampCard = () => {
  showStampCard.value = false;
};

// タイマーをセットする関数
const setGhostTimer = () => {
  if (ghostTimer) clearTimeout(ghostTimer);
  
  if (charState.value !== 'idle' || spinning.value) return;

  ghostTimer = setTimeout(() => {
    console.log("Ghost animation start!"); // これを足してコンソールで確認
    startCharAnimation();
  }, 5000); // テスト用に5秒 // 1分（60秒）60000
};



onMounted(() => {
  const savedStamps = JSON.parse(localStorage.getItem('stampHistory') || '[]')
  const lastDate = localStorage.getItem('lastSpinDate')
  const count = parseInt(localStorage.getItem('dailyCount') || '0')
  const today = new Date().toISOString().split('T')[0]
  const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0]
  const savedStreak = parseInt(localStorage.getItem('streakCount') || '0')
  const allSaved = JSON.parse(localStorage.getItem('stampHistory') || '[]')
  

  // 画面に表示するスタンプ帳（stamps.value）は常に直近7日分
  stamps.value = allSaved.slice(-7)
  // ストリークの判定
  // 今日の1回目ならストリーク更新
  if (lastDate === today) {
    dailyCount.value = count
    streakCount.value = savedStreak
  } else if (lastDate === yesterday) {
    // 昨日やっていたら継続
    streakCount.value = savedStreak
  } else {
    // 1日空いたらリセット
    streakCount.value = 0
    localStorage.setItem('streakCount', '0')
  }

  setGhostTimer();
})

const startCharAnimation = () => {
  // 1. まず移動開始（5秒かけて歩く）
  charState.value = 'moving';

  // 2. 移動アニメーション終了に合わせてジャンプ開始
  setTimeout(() => {
    charState.value = 'jumping';
  }, 5000);

  // 3. ジャンプ終了後、移動開始
  setTimeout(() => {
    charState.value = 'climbing'; 
  }, 8000);

  // 4. 移動完了後、静止
  setTimeout(() => {
    charState.value = 'finished';
  }, 9000);
};

// お化けをクリックした時の処理（消えたあと、また1分タイマーを再開）
const handleCharClick = () => {
  if (isClicked.value) return;
  isClicked.value = true;
  
  setTimeout(() => {
    isClicked.value = false;
    charState.value = 'idle';
    setGhostTimer(); // 成仏したあと、また1分待機へ
  }, 3000);
};

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

const spin = async () => {
  if (spinning.value) return

  // ★ ルーレットを回したら「放置」ではなくなるので、タイマーをキャンセル
  if (ghostTimer) clearTimeout(ghostTimer);

  // もしお化けが出ている最中だったら強制的に消す
  charState.value = 'idle';
  isClicked.value = false;

  // 音の再生（ループ設定）
  spinSe.loop = true
  spinSe.currentTime = 0
  spinSe.play()

  spinning.value = true
  
  const result = drawExercise()
  
  const sectorAngle = 360 / 5
  const targetLevelIndex = result.level - 1
  const additionalRotation = 360 * 5 - (targetLevelIndex * sectorAngle)
  const currentActualRotation = rotation.value % 360
  rotation.value += (additionalRotation - currentActualRotation)

  // ルーレットの回転計算
   // 1. ルーレットが止まるのを待つ (2.5秒)
   await new Promise(resolve => setTimeout(resolve, 2500))

// ★ ここに追加：ルーレットが止まってから「さらに1秒」音を鳴らし続ける場合
// await new Promise(resolve => setTimeout(resolve, 1000))

  // 止まったら音を切り替える
  spinSe.pause()
  winSe.currentTime = 0
  winSe.play()

  // 2. 止まってから結果を表示
  exerciseResult.value = result
  spinning.value = false

  updateProgress(result)

  const today = new Date().toISOString().split('T')[0]
  const lastDate = localStorage.getItem('lastSpinDate')
  
  if (lastDate !== today) {
    saveResult(result)
  }

  // 3. メニューが出てから「1.5秒後」にスタンプ台へ
  await new Promise(resolve => setTimeout(resolve, 1500))
  
  if (exerciseResult.value) {
    confirmResult()
  }
  // 抽選が始まった（または終わった）タイミングでお化けを予約
  sendNotificationTaskToSW();
}

function drawExercise() {
  // レベルの重み付け
  // const RARE_RATE = 0.2
  // fixedな0.2ではなく、computedの確率を使う
  const isRare = Math.random() < currentRareRate.value
  const levelPool = isRare ? [4, 5] : [1, 2, 3]
  const level = levelPool[Math.floor(Math.random() * levelPool.length)]
  

  // 【重要】用意したリストからランダムに1つ選んでいます
  const list = exerciseLevels[level]
  const randomIndex = Math.floor(Math.random() * list.length)
  const text = list[randomIndex]

  return { 
    level: level, 
    text: text 
  }
}


const saveResult = (result) => {
  const today = new Date().toISOString().split('T')[0]
  
  const newStamp = {
    date: today,
    level: result.level,
    symbol: symbols[result.level - 1],
    count: 1 // 初回なので1
  }
  
  // 全履歴を取得して新しいのを追加
  let allStamps = JSON.parse(localStorage.getItem('stampHistory') || '[]')
  allStamps.push(newStamp)
  
  // 保存は30日分、表示は7日分
  const forStorage = allStamps.slice(-30)
  localStorage.setItem('stampHistory', JSON.stringify(forStorage))
  localStorage.setItem('lastSpinDate', today)
  
  stamps.value = forStorage.slice(-7) // 画面のスタンプ帳は7個だけ
  canSpinToday.value = false 
}
const updateProgress = (result) => {
  const today = new Date().toISOString().split('T')[0]
  
  dailyCount.value += 1
  localStorage.setItem('dailyCount', dailyCount.value.toString())
  window.dispatchEvent(new Event('spin-updated'))
  
  // 1. 全ての履歴（最大30日分）を取得
  let savedStamps = JSON.parse(localStorage.getItem('stampHistory') || '[]')
  let todayStamp = savedStamps.find(s => s.date === today)

  if (!todayStamp) {
    todayStamp = {
      date: today,
      level: result.level,
      symbol: symbols[result.level - 1],
      count: dailyCount.value,
      hasBadge: false,
      // 1回目の運動を配列に入れる
      logs: [{ level: result.level, text: result.text, time: new Date().toLocaleTimeString() }]
    }
    savedStamps.push(todayStamp)
  } else {
    todayStamp.count = dailyCount.value
    todayStamp.level = result.level // カレンダー用には最新（または最高）レベルを表示
    todayStamp.symbol = symbols[result.level - 1]

    // 2回目以降の運動を配列に追加する
    if (!todayStamp.logs) todayStamp.logs = [] // 古いデータがある場合用
    todayStamp.logs.push({ 
      level: result.level, 
      text: result.text, 
      time: new Date().toLocaleTimeString() 
    })
    
    if (dailyCount.value >= 3) todayStamp.hasBadge = true
  }

  // 保存用：直近30日分を残す
  const forStorage = savedStamps.slice(-31)
  localStorage.setItem('stampHistory', JSON.stringify(forStorage))
  localStorage.setItem('lastSpinDate', today)

  // 表示用（スタンプ帳）：直近7日分だけを反映
  stamps.value = forStorage.slice(-7)
  // -------------------------

  if (dailyCount.value >= 3) {
    saveBadge(today)
  }
}


const saveBadge = (date) => {
  // 今日のスタンプデータにバッジフラグを立てる
  let updated = stamps.value.map(s => {
    if (s.date === date) return { ...s, hasBadge: true }
    return s
  })
  // ステートとローカルストレージの両方を更新
  stamps.value = updated
  localStorage.setItem('stampHistory', JSON.stringify(updated))
  hasBadgeToday.value = true
}
// 今日のトレーニングをシェア

const shareResult = async () => {
  // 1. 画像化したい範囲の要素を取得
  const element = document.getElementById('share-area');
  
  // 2. 要素をキャンバスに描画してBlob（画像データ）に変換
  const canvas = await html2canvas(element, {
    backgroundColor: '#FFFDE7', // ヘッダーと同じ背景色を指定
    useCORS: true // ロゴ画像などの読み込みを許可
  });
  
  canvas.toBlob(async (blob) => {
    const file = new File([blob], 'FitSpin_Result.png', { type: 'image/png' });
    
    // 3. Web Share APIでシェア
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'FitSpin 今日のレベル',
          text: '今日のトレーニングレベルはこれ！',
          files: [file], // 生成した画像を添付
        });
      } catch (error) {
        console.error('シェアに失敗しました', error);
      }
    } else {
      // シェア非対応ブラウザ（PCなど）の場合は画像をダウンロードさせる
      const link = document.createElement('a');
      link.href = canvas.toDataURL();
      link.download = 'FitSpin_Result.png';
      link.click();
    }
  });
};



</script>

<template>
  <div class="gacha-container">
    <h2 style="color: black;"></h2>

    <div v-if="streakCount > 0" class="streak-badge">
      🔥 {{ streakCount }}日連続！ (レア率 {{ Math.floor(currentRareRate * 100) }}%)
    </div>




    <div class="roulette-wrapper">

      <!-- progress bar 1回目:（120度）/2回目:（240度）3回目: 一周！  -->
      <svg class="progress-ring" viewBox="0 0 400 400">
  <circle
    class="progress-ring__background"
    stroke="rgba(255, 255, 255, 0.3)" 
    stroke-width="4"
    fill="transparent"
    r="180" 
    cx="200" 
    cy="200"
  />
  <circle
    class="progress-ring__circle"
    stroke="#FF00FF" 
    stroke-width="8" 
    stroke-linecap="round"
    fill="transparent"
    r="180" 
    cx="200" 
    cy="200"
    :style="progressBarStyle"
  />
</svg>
      <div class="pointer">▼</div>

      <button @click="spin" class="gacha-button" :disabled="spinning">
        {{ spinning ? '抽選中...' : 'PUSH' }}
      </button>

      <div 
        class="roulette-wheel"
        :style="{ transform: `rotate(${rotation}deg)` }"
      >
        <div
          v-for="level in 5"
          :key="level"
          class="roulette-sector"
          :style="getSectorStyle(level - 1)"
        >
          <div class="sector-content">
            <span class="symbol">{{ symbols[level - 1] }}</span>
            <span class="level-label">Lv.{{ level }}</span>
          </div>
        </div>
      </div>

<!-- ghost -->
<div v-if="!spinning && !exerciseResult" class="pressure-ghost-fixed">
  <img src="@/assets/logo/ghost.png" alt="Ghost" class="ghost-img-mini" />
  <div class="char-speech-mini">早く回そ？</div>
</div>

<div 
  v-if="!spinning && !exerciseResult"
  class="char-actor"
  :class="[charState, { 'is-fading': isClicked }]"
  @click="handleCharClick" 
>
        <img src="@/assets/logo/ghost.png" alt="Ghost" class="char-img" />
        
        <div v-if="charState === 'finished'" class="char-speech">
          押す？押さない？
        </div>
      </div>

      <Transition name="fade-scale">
        <div v-if="exerciseResult && !spinning" class="result-overlay">
          <div id="share-area" class="result-card">
            <div class="level-badge">Lv.{{ exerciseResult.level }}</div>
            <h3>本日のメニュー</h3>
            <div class="exercise-text">{{ exerciseResult.text }}</div>
            <div class="result-actions">
              <button @click="shareResult" class="share-button">
                📱 シェア
              </button>

            <button @click="exerciseResult = null" class="close-button">OK!</button>
          </div>
          </div>
        </div>
      </Transition>

      <!-- スタンプカード表示 -->
      <!-- <button @click="confirmResult" class="close-button">OK!</button> -->

      <Transition name="fade-slide">
      <div v-if="showStampCard" class="stamp-card-overlay">
        <div class="stamp-card">
          <div class="stamp-header">
            <h3>7 Days Challenge</h3>
            <div class="count-viewer">Today: {{ dailyCount }} / 3</div>
          </div>
          
          <div class="stamp-grid">
            <div v-for="n in 7" :key="n" class="stamp-slot" :class="{ 'is-active': stamps[n-1] }">
              <div v-if="stamps[n-1]" class="stamp-content is-stamped">
                <img :src="circleLarge"  class="cell-img large" v-if="stamps[n-1].count >= 3" />
                <img :src="circleMedium" class="cell-img medium" v-if="stamps[n-1].count >= 2" />
                <img :src="circleSmall"  class="cell-img small" v-if="stamps[n-1].count >= 1" />
              </div>
              <span v-else class="empty-slot">{{ n }}</span>
            </div>
          </div>
          
          <p v-if="dailyCount >= 3" class="congrats-msg">✨ 本日の特別バッジ獲得！ ✨</p>
          <button @click="closeStampCard" class="back-button">閉じる</button>
        </div>
      </div>
    </Transition>
    </div>
  </div>
</template>



<style scoped>
.gacha-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-bottom: 20px;
}

.roulette-wrapper {
  position: relative;
  width: 300px;
  height: 300px;
  /* 上下の余白を小さくして、スクロールなしでも見えるように調整 */
  margin: 20px auto 40px auto; 
  max-width: 90vw; /* 画面からはみ出さないように */
}

.roulette-wheel {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  position: relative;
  transition: transform 2s cubic-bezier(0.15, 0, 0.15, 1);
  border: 4px solid #2D3436; /* 太めの境界線 */
  box-shadow: 4px 4px 0px #2D3436; /* ベタ塗りの影 */
  overflow: hidden;
  z-index: 20;

  /* 80's ポップな配色 */
  background: conic-gradient(
    from -36deg,
    #FF6B6B 0deg 72deg,    /* Lv.1 */
    #4ECDC4 72deg 144deg,  /* Lv.2 */
    #FFD93D 144deg 216deg, /* Lv.3 */
    #6C5CE7 216deg 288deg, /* Lv.4 */
    #FF85A2 288deg 360deg  /* Lv.5 */
  );
}

.roulette-sector {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 60px;
  margin-left: -30px;
  margin-top: -30px;
  text-align: center;
}

.sector-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* ルーレット内の絵文字スタイル */
.symbol {
  font-size: 38px; /* 少し大きく */
  display: inline-block;
  /* 80's風のステッカー加工（白縁取り＋黒影） */
  filter: 
    drop-shadow(2px 0 0 white) 
    drop-shadow(-2px 0 0 white) 
    drop-shadow(0 2px 0 white) 
    drop-shadow(0 -2px 0 white)
    drop-shadow(4px 4px 0px #2D3436);

  margin-bottom: 5px;
}
.level-label { font-size: 12px; font-weight: bold; color: #333; }

.pointer {
  position: absolute;
  top: -25px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 32px;
  color: #2D3436;
  z-index: 30;
  text-shadow: 2px 2px 0px white;
}

.gacha-button {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 40;
  width: 85px;
  height: 85px;
  cursor: pointer;
  background: #FFF;
  border: 4px solid #2D3436;
  border-radius: 50%;
  font-weight: 900;
  font-size: 14px;
  color: #2D3436;
  box-shadow: 4px 4px 0px #2D3436;
  transition: all 0.1s;
}

.gacha-button:active {
  transform: translate(-46%, -46%);
  box-shadow: 0px 0px 0px #2D3436;
}


.result-area {
  margin-top: 30px;
  text-align: center;
  animation: fadeIn 0.5s ease;
}

/* ルーレットの親要素に対して絶対座標で重ねる */
.result-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
  /* 背景を少し暗くして結果を際立たせる */
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(4px);
  border-radius: 50%;
}

/* 結果カードのデザイン */
.result-card {
  background: white;
  padding: 30px;
  border-radius: 20px;
  border: 4px solid #2D3436;
  box-shadow: 10px 10px 0px #2D3436;
  text-align: center;
  width: 85%;
}

.level-badge {
  background: #FFD93D;
  color: #2D3436;
  border: 2px solid #2D3436;
  padding: 5px 15px;
  border-radius: 10px;
  font-weight: 900;
  margin-bottom: 15px;
}

.exercise-text {
  font-size: 20px;
  font-weight: bold;
  margin: 15px 0;
  color: #333;
}

.close-button {
  background: #333;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 10px;
  cursor: pointer;
}

/* 出現アニメーション：ふわっと大きくなる */
.fade-scale-enter-active, .fade-scale-leave-active {
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.fade-scale-enter-from {
  opacity: 0;
  transform: scale(0.5);
}

.fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.8);
}

/* スタンプカードをオーバーレイ（最前面）にする */
.stamp-card-overlay {
  position: absolute;
  top: 0; /* 0に調整してカードの重なりを綺麗に */
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  z-index: 150;
  display: flex;
  justify-content: center;
}

/* スタンプ台が表示されている間、後ろのルーレットを少し透かして「重なり感」を出す */
.stamp-card-overlay::before {
  content: "";
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  backdrop-filter: blur(2px);
  z-index: -1;
}

/* 戻るボタンのスタイル */
.back-button {
  margin-top: 20px;
  background: #eee;
  color: #333;
  border: 2px solid #333;
  padding: 6px 15px;
  border-radius: 10px;
  font-weight: bold;
  cursor: pointer;
  font-size: 12px;
}

/* スタンプカードのデザイン変更 */
.stamp-card {
  width: 90%;
  max-width: 400px;
  background: #ffffff;
  padding: 24px;
  border-radius: 20px;
  border: 4px solid #2D3436;
  box-shadow: 8px 8px 0px #2D3436;
}


.stamp-content {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}



/* --- スタンプカード全体のレイアウト --- */
.stamp-grid {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  margin-top: 25px;
}


/* --- 1. 親（スロット）のサイズを大きく固定 --- */
.stamp-slot {
  position: relative;
  /* 枠（グレーの丸）のサイズをスタンプより小さく設定 */
  /* ここを小さくすることで、スタンプとの比率が下がります */
  width: 28px !important;  
  height: 28px !important;
  
  border-radius: 50%;
  background: #333 !important;
  border: 1px solid #555 !important;
  flex-shrink: 0;

  
  /* Flexを解除し、中身の絶対配置に任せます */
  display: block !important;
}

/* --- 2. スタンプ画像：枠のサイズに依存せず、44pxを維持して正中に置く --- */
.cell-img {
  position: absolute !important;
  /* 親（28px）より大きなサイズ（44px）を直接指定 */
  /* これにより、枠を小さくしてもスタンプは小さくなりません */
  width: 44px !important;
  height: 44px !important;
  
  /* 常に「枠の真ん中」を基準に配置 */
  top: 50% !important;
  left: 53% !important;
  transform: translate(-50%, -45%) !important;
  
  object-fit: contain;
  margin: 0 !important;
  padding: 0 !important;
  display: block !important;
}

/* 重なり順 */
.cell-img.large  { z-index: 1; }
.cell-img.medium { z-index: 2; }
.cell-img.small  { z-index: 3; }

/* 数字（n）の配置 */
.empty-slot {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 11px;
  color: #666;
}

.main-symbol-overlay {
  position: absolute;
  z-index: 4;
  font-size: 14px;
  /* 円の上で見えやすいように調整 */
  text-shadow: 0 0 4px rgba(0,0,0,0.8);
}

.special-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  font-size: 16px;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
  animation: bounce 0.5s ease infinite alternate;
}

.count-viewer {
  color: #6C5CE7;
  font-weight: 900;
  font-size: 14px;
}

@keyframes bounce {
  from { transform: translateY(0); }
  to { transform: translateY(-3px); }
}

.limit-msg {
  color: #ff4757;
  font-size: 12px;
  margin-top: 10px;
  font-weight: bold;
}

@keyframes pop {
  0% { transform: scale(0); }
  100% { transform: scale(1); }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* スタンプカードが出現する時のアニメーション */
.fade-slide-enter-active, .fade-slide-leave-active {
  transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translate(-50%, 20px); /* 下からふわっと */
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translate(-50%, -10px) scale(0.9);
}

/* シェアボタン */
.result-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
}

.share-button {
  background: #6C5CE7;
  color: white;
  border: 2px solid #2D3436;
  padding: 8px 15px;
  border-radius: 10px;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 2px 2px 0px #2D3436;
}

/* 3日連続！ボーナスコメント */
.streak-badge {
  background: #FFD93D; /* 黄色ベース */
  color: #2D3436;
  border: 2px solid #2D3436;
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: 900;
  font-size: 13px;
  margin-bottom: 10px;
  box-shadow: 3px 3px 0px #2D3436;
  animation: pulse 2s infinite; /* 少し動かすと目立つ */
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}



/* --- キャラクターアニメーション 決定版 --- */

.char-actor {
  position: absolute;
  top: 50%;
  /* ラップトップでも外に見えるよう、ビューポートの左端よりさらに外(-60vw)に設定 */
  left: -60vw; 
  transform: translateY(-50%);
  z-index: 35;
  width: 70px;
  height: auto;
  opacity: 0;
  cursor: pointer; /* 触れることを示唆 */
}

.char-img {
  width: 100%;
  height: auto;
  display: block;
  filter: hue-rotate(90deg) brightness(1.2) saturate(1.5);
}

/* 1. 画面外から中央下へトコトコ歩く */
.char-actor.moving {
  opacity: 1;
  /* 5秒かけて、等速(linear)に近い形でゆっくり動かす */
  animation: moveInFromFarLeft 5s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

/* 2. 中央でジャンプ */
.char-actor.jumping {
  opacity: 1;
  left: 50%; 
  z-index: 41; 
  transform: translate(-50%, 110px);
  animation: jumpThreeTimes 3s ease-in-out forwards;
}

/* 3. ルーレットの裏を通って左上へ */
.char-actor.climbing {
  opacity: 1;
  left: 50%;
  /* z-index を 5 から 16 にアップ（プログレスバー 15 の手前） */
  z-index: 16;
  animation: climbToBackDiagonal 1s ease-in-out forwards;
}

/* 4. 最終状態：斜めにひょっこり */
.char-actor.finished {
  opacity: 1;
  left: 50%;
  /* z-index を 5 から 16 にアップ（プログレスバー 15 の手前） */
  z-index: 16;
  transform: translate(calc(-50% - 120px), -145px) rotate(-30deg);
  animation: breatheDiagonal 2s infinite alternate;
}

/* 吹き出し（お化けよりさらに手前、でもルーレットよりは後ろ） */
.char-speech {
  position: absolute;
  top: -35px;
  left: 50%;
  transform: translateX(-50%) rotate(30deg);
  /* お化け本体(16)より大きく、ルーレット(20)より小さい値に */
  z-index: 17; 
  background: white;
  border: 2px solid #2D3436;
  padding: 4px 10px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: bold;
  white-space: nowrap;
  box-shadow: 2px 2px 0px rgba(0,0,0,0.2);
}
/* --- Keyframes --- */



/* アニメーション定義も5秒に合わせてスムーズに */
@keyframes moveInFromFarLeft {
  0% { 
    left: -80vw; /* さらに遠くからスタートさせて余裕を持たせる */
    transform: translate(0, 110px); 
  }
  100% { 
    left: 50%;
    transform: translate(-50%, 110px);
  }
}
/* ジャンプ（位置を固定） */
@keyframes jumpThreeTimes {
  0%, 33.3%, 66.6%, 100% { transform: translate(-50%, 110px); }
  16.6%, 50%, 83.3% { transform: translate(-50%, 40px); }
}

/* 対角線上に裏を通る */
@keyframes climbToBackDiagonal {
  0% { transform: translate(-50%, 110px) rotate(0deg); }
  100% { transform: translate(calc(-50% - 120px), -145px) rotate(-30deg); }
}

/* 呼吸 */
@keyframes breatheDiagonal {
  from { transform: translate(calc(-50% - 120px), -145px) rotate(-30deg) scale(1); }
  to { transform: translate(calc(-50% - 120px), -143px) rotate(-30deg) scale(1.03); }
}

/* 「3秒かけて消える」アニメーションを定義 */
.char-actor.is-fading {
  transition: opacity 3s ease-out, transform 3s ease-out !important; /* アニメーションを優先 */
  opacity: 0 !important;
  transform: translate(calc(-50% - 120px), -180px) scale(1.5) !important; /* 斜め位置からさらに浮上 */
  pointer-events: none; /* 消えている最中はクリック不可 */
}

/* マウスを乗せた時に「触れる」ことを教える（ラップトップ向け） */
.char-actor:not(.is-fading) {
  cursor: pointer;
}

/* 右下常駐お化けのスタイル */
.pressure-ghost-fixed {
  position: absolute;
  /* ルーレットの枠外、右斜め下のデッドスペースへ */
  right: -60px; 
  bottom: -70px;
  width: 50px;
  z-index: 10;
  opacity: 0.8;
  pointer-events: none;
  /* 左右に均等に揺れるアニメーション */
  animation: pressureSwing 2s infinite ease-in-out;
}

.ghost-img-mini {
  width: 100%;
  filter: hue-rotate(90deg) brightness(1.2);
}

.char-speech-mini {
  position: absolute;
  top: -25px;
  left: -20px;
  background: #FFD93D;
  border: 2px solid #2D3436;
  padding: 2px 8px;
  border-radius: 8px;
  font-size: 10px;
  font-weight: bold;
  white-space: nowrap;
  box-shadow: 2px 2px 0px rgba(0,0,0,0.2);
}

/* 左右の揺れ幅を少し抑えて、より自然なスイングに調整 */
@keyframes pressureSwing {
  0% { 
    transform: translateX(-5px) rotate(-8deg); 
  }
  50% { 
    transform: translateX(5px) rotate(8deg); 
  }
  100% { 
    transform: translateX(-5px) rotate(-8deg); 
  }
}

/* --- 見た目だけを80sに変える修正 --- */

.progress-ring {
  position: absolute;
  width: 400px;
  height: 400px;
  top: 0;
  left: 0;
  margin-top: -44px; /* Marikoさんの位置調整を維持 */
  margin-left: -44px; /* Marikoさんの位置調整を維持 */
  transform: rotate(-90deg);
  display: block;
  z-index: 15;
  pointer-events: none;
  overflow: visible; 

}

.progress-ring__background {
  /* [修正] 透過ホワイトから、ルーレットの境界線と同じダークグレーへ */
  stroke: #2D3436 !important; 
  stroke-width: 4; /* ルーレットの border: 4px と太さを統一 */
  fill: transparent;
}

.progress-ring__circle {
  transform: translate(0.5px, 0.5px);
  
  /* [修正] 進捗の色をマゼンタに固定し、太くして目立たせる */
  stroke: #FF00FF !important; 
  stroke-width: 10; /* 背景の線より少し太くすると重なりが綺麗です */
  stroke-linecap: round;
  fill: transparent;
  
  /* [削除] ネオンの発光（Glow）エフェクトを完全に除去 */
  /* filter: drop-shadow(0 0 4px #FF00FF); ←これを消す */
  
  transition: stroke-dashoffset 0.8s ease-in-out;
}

/* 
z-index の設計図
背景: 0

プログレスバー: 15

待機ゴースト: 16 〜 18 くらい

ルーレット本体: 20

ルーレットの針やボタン: 30 以上
*/
</style>