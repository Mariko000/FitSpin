<script setup>
import { ref, onMounted, computed,watch, onUnmounted } from 'vue'
import { exerciseLevels } from '../exercise/exercise_levels.js'
import { useExerciseStore } from '../stores/useExerciseStore' // Storeをインポート
import StampCard from '@/components/StampCard.vue'
import { useWeather } from '@/envContext'

// 画像・音声アセット
// TENKI
import sunnyImg from '@/assets/css/TENKI/sunny.PNG'
import cloudyImg from '@/assets/css/TENKI/cloudy.PNG'
import raindropImg from '@/assets/css/TENKI/raindrop.PNG'

import circleSmall from '../assets/images/badges/cell-circle_small.png'
import circleMedium from '../assets/images/badges/cell-circle_medium.png'
import circleLarge from '../assets/images/badges/cell-circle_large.png'
import spinSePath from '../assets/sounds/spin.mp3'
import winSePath from '../assets/sounds/win.mp3'

// 今日のトレーニングをシェア
import html2canvas from 'html2canvas';

// 23:59
// ↓
// 00:00 ← ここで自動発火
// ↓
// dailyCount リセット
// lastSpinDate 更新
// レア率再計算
// 天気再取得
// 画面更新

// --- Storeのセットアップ ---
const store = useExerciseStore() //

const stamps = ref([])

// 日付監視ループ
let dateCheckTimer = null

// TENKI
const DEBUG_WEATHER = true
// テストしたい過去日付
const TEST_DATE = '2026-05-01'
// const weatherType = ref('sunny')

const {
  weatherType,
  fetchWeather,
  fetchPastWeather,
} = useWeather()

// --- キャラクター・ルーレット状態管理 ---
const showIntro = ref(false);
const showGhost = ref(true); // ★ お化けと吹き出しの表示状態を管理するフラグを追加
const isGhostFading = ref(false); // ★ フェードアウト用クラス制御のフラグ
const charState = ref('idle');
const isClicked = ref(false);
let ghostTimer = null;

// ★セリフのバリエーション
const greetings = [
  "僕はスピまる！一緒に頑張ろう！",
  "お疲れさま。少し動かない？",
  "1週間続けたら、いいものあげるね！",
  "肩、回してみない？",
  "無理せず自分のペースでね。"
];

// 現在表示するセリフ
const charSpeechText = ref("早く回そ？");

const rotation = ref(0)
const spinning = ref(false)
const exerciseResult = ref(null)
const showStampCard = ref(false);

const symbols = store.symbols // Storeから取得


// --- Audio Objects ---
const spinSe = new Audio(spinSePath)
const winSe = new Audio(winSePath)


// --- Storeの変更を検知して音量を即時反映 ---
watch(
  [() => store.volume, () => store.isMuted],
  ([newVol, newMuted]) => {
    const actualVolume = newMuted ? 0 : newVol;
    spinSe.volume = actualVolume;
    winSe.volume = actualVolume;
  },
  { immediate: true }
)

// --- Computed ---
// 進捗バーの計算
const progressBarStyle = computed(() => {
  const max = 3;
  const radius = 180;
  const circumference = 2 * Math.PI * radius;
  // store.dailyCountを参照するように変更
  const offset = circumference - (Math.min(store.dailyCount, max) / max) * circumference;
  return {
    strokeDasharray: circumference,
    strokeDashoffset: offset,
    transition: 'stroke-dashoffset 0.8s ease-in-out'
  };
});

// レア率をStoreから取得
const currentRareRate = computed(() => store.currentRareRate)


// Open-Meteo取得関数
const WEATHER_KEY = 'fitspin_weather'
const WEATHER_DATE_KEY = 'fitspin_weather_date'

// 現在位置取得関数
/*const getCurrentLocation = () => {
  return new Promise((resolve, reject) => {

     console.log('位置情報取得開始')

    navigator.geolocation.getCurrentPosition(

      //成功時
      (position) => {

        console.log('位置情報取得成功')

        resolve({
          lat: position.coords.latitude,
          lon: position.coords.longitude
        })
      },

      // 失敗時
    (error) => {

       console.error('位置情報取得失敗', error)

       reject(error)
      },

      //// オプション
      {
        enableHighAccuracy: true,
        timeout: 5000,
        maximumAge: 0
      }
    )
 })
}

const getLocationInfo = async () => {
  const { lat, lon } = await getCurrentLocation()

  const location = await getLocationName(lat, lon)

  return {
    lat,
    lon,
    location
  }
}

// 地名取得の逆ジオコーディング
const getLocationName = async (lat, lon) => {
  try {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`
    )

    const data = await response.json()

    return {
      country: data.address.country,
      prefecture:
        data.address.state ||
        data.address.region ||
        data.address.county,
      city:
        data.address.city ||
        data.address.town ||
        data.address.village
    }

  } catch (error) {
    console.error('地名取得失敗', error)

    return null
  }
}

// 天気
const fetchWeather = async () => {
  const today = new Date().toISOString().split('T')[0]

  console.log('天気取得開始')

  try {
    const { lat, lon, location } = await getLocationInfo()

    const response = await fetch(
      `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=weather_code`
    )

    const data = await response.json()
    const code = data.current.weather_code

    let type = 'sunny'

    if ([0, 1].includes(code)) {
      type = 'sunny'
    } else if ([2, 3, 45, 48].includes(code)) {
      type = 'cloudy'
    } else {
      type = 'rainy'
    }

    weatherType.value = type

    // --- ここから追加：コンソール確認用 ---
    console.log('===== 現在の天気データ =====')
    console.log('取得日時:', new Date().toLocaleString())
    console.log('現在位置:', { latitude: lat, longitude: lon })
    console.log('地名:', location)
    console.log('weather_code (raw):', code)
    console.log('判定結果 (weatherType):', type)
    console.log('APIレスポンス全文:', data)
    console.log('==========================')

  } catch (error) {
    console.error('天気取得失敗', error)
    weatherType.value = 'sunny'
  }
}

// 過去天気取得関数　*テスト用
const fetchPastWeather = async (date) => {
  console.log(`--- 過去天気取得テスト開始: ${date} ---`);
  try {
    // 1. 位置情報の取得を待つ
    const { lat, lon, location } = await getLocationInfo();

    // 2. Archive APIを叩く（timezoneを Asia/Tokyo に指定）
    const response = await fetch(
      `https://archive-api.open-meteo.com/v1/archive?latitude=${lat}&longitude=${lon}&start_date=${date}&end_date=${date}&daily=weather_code&timezone=Asia%2FTokyo`
    );

    if (!response.ok) throw new Error('ネットワーク応答が正常ではありません');
    
    const data = await response.json();
    console.log('APIレスポンス詳細:', data);

    // 3. データの取り出し（daily配下の配列の 0番目）
    if (!data.daily || !data.daily.weather_code) {
      throw new Error('指定した日付のデータが見つかりません');
    }
    
    const code = data.daily.weather_code[0];
    let type = 'sunny';

    // 判定ロジック
    if ([0, 1].includes(code)) {
      type = 'sunny';
    } else if ([2, 3, 45, 48].includes(code)) {
      type = 'cloudy';
    } else {
      type = 'rainy';
    }

    // 4. リアクティブ変数にセット（ここで背景が変わるはず！）
    weatherType.value = type;

    console.log('===== 天気テスト結果 =====');
    console.log('日付:', date);
    console.log('場所:', location?.city || '不明');
    console.log('weather_code:', code);
    console.log('変換結果 (weatherType):', type);
    console.log('==========================');

    return `完了: ${type}`; // コンソールに結果を表示させるため

  } catch (error) {
    console.error('過去天気取得失敗:', error.message);
  }
};
*/

// --- Functions ---
const getSectorStyle = (index) => {
  const totalSectors = 5
  const angle = 360 / totalSectors
  return {
    transform: `rotate(${angle * index}deg) translateY(-110px) rotate(${-angle * index}deg)`
  }
}

const confirmResult = () => {
  exerciseResult.value = null;
  showStampCard.value = true;
};

const closeStampCard = () => {
  showStampCard.value = false;
};

// お化けタイマー
const setGhostTimer = () => {
  if (ghostTimer) clearTimeout(ghostTimer);
  if (charState.value !== 'idle' || spinning.value) return;
  ghostTimer = setTimeout(() => {
    startCharAnimation();
  }, 60000); // 1分
};

// 日付監視ループ
const startDateWatcher = () => {
  dateCheckTimer = setInterval(async () => {

    const today = store.getTodayJST()

    // 日付変更検知
    if (store.lastSpinDate !== today) {

      console.log('日付変更を検知')

      // Store更新
      store.initialize()

      // 天気更新
      await fetchWeather()

      // UIイベント
      window.dispatchEvent(new Event('date-changed'))
    }

  }, 60000) // 1分ごと確認
}

// お化けのタイマーではなく、アプリを立ち上げた瞬間に、一度だけ外の天気をカンニングしに行くための処理
onMounted(async () => {
  // 1. 保存されているデータを復元
  store.initialize()

  // 2. 日付を跨いでいたらカウントをリセット
  startDateWatcher()

  // 3. お化けの自動移動タイマー（1分間放置で発動）を開始
  setGhostTimer()

  // 4. 現在地の天気を取得して反映
  await fetchWeather()
})

// アプリ開きっぱなし対策
onUnmounted(() => {
  if (dateCheckTimer) {
    clearInterval(dateCheckTimer)
  }
})

// DevTools Console にこれ打つだけ：fetchPastWeather('2025-12-25')
window.fetchPastWeather = fetchPastWeather


//待機時間に動くアニメーション
const startCharAnimation = () => {
  charState.value = 'moving';
  setTimeout(() => { charState.value = 'jumping'; }, 5000);
  setTimeout(() => { charState.value = 'climbing'; }, 8000);
  setTimeout(() => { charState.value = 'finished'; }, 9000);
};

// ① お化けクリック用（ランダム挨拶の適用 ＋ 3秒表示の維持アニメーション）
const handleGhostClick = () => {
  if (!showGhost.value || isGhostFading.value) return;

  // 1. 既存のセリフ（greetings）をコピー
  let currentPool = [...greetings];

  // 2. 現在の天気（weatherType）に応じたセリフをプールに追加
  if (weatherType.value === 'sunny') {
    currentPool.push("外はいい天気！窓を開けて運動しよ？");
    currentPool.push("お日様が出てると、なんだかやる気が出るね！");
  } else if (weatherType.value === 'cloudy') {
    currentPool.push("どんよりお天気だけど、体は軽く動かしておこう？");
    currentPool.push("外が暗い分、画面の中は明るく回しちゃおう！");
  } else if (weatherType.value === 'rainy') {
    currentPool.push("雨の音を聞きながら、お家でストレッチしよ？");
    currentPool.push("外に行けない日は、スピまるの出番だね！");
  }

  // 3. 合体したプールの中からランダムに選ぶ
  const randomIndex = Math.floor(Math.random() * currentPool.length);
  charSpeechText.value = currentPool[randomIndex];

  // --- 以降は既存の表示・フェード処理 ---
  showIntro.value = true;
  setTimeout(() => {
    isGhostFading.value = true;
    setTimeout(() => {
      showGhost.value = false;
      isGhostFading.value = false;
    }, 1000);
  }, 2500);

  setTimeout(() => {
    charSpeechText.value = "早く回そ？";
    showIntro.value = false;
    showGhost.value = true;
  }, 6500); 
};

// ② 待機時間を経て画面上に移動するキャラクタークリック用（フェードアウトのみ）
const handleCharClick = () => {
  if (isClicked.value) return;

  // フェードアウトのアニメーションを発動
  isClicked.value = true;

  // 3秒後にリセット
  setTimeout(() => {
    isClicked.value = false;
    charState.value = 'idle';
    setGhostTimer(); // タイマー再開
  }, 3000);
};



const drawExercise = () => {
  const isRare = Math.random() < currentRareRate.value
  const levelPool = isRare ? [4, 5] : [1, 2, 3]
  const level = levelPool[Math.floor(Math.random() * levelPool.length)]
  const list = exerciseLevels[level]
  const text = list[Math.floor(Math.random() * list.length)]
  return { level, text }
}

const spin = async () => {
  if (spinning.value) return
  if (ghostTimer) clearTimeout(ghostTimer);
  charState.value = 'idle';
  isClicked.value = false;

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

  await new Promise(resolve => setTimeout(resolve, 2500))

  spinSe.pause()
  winSe.currentTime = 0
  winSe.play()

  exerciseResult.value = result
  spinning.value = false

  // ★ Storeへ結果を記録（localStorage保存もここで行われる）
  store.addExerciseRecord(result)

  await new Promise(resolve => setTimeout(resolve, 1500))
  if (exerciseResult.value) {
    confirmResult()
  }
}

const shareResult = async () => {
  const element = document.getElementById('share-area');
  const canvas = await html2canvas(element, {
    backgroundColor: '#FFFDE7',
    useCORS: true
  });
  
  canvas.toBlob(async (blob) => {
    const file = new File([blob], 'FitSpin_Result.png', { type: 'image/png' });
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'FitSpin 今日のレベル',
          text: '今日のトレーニングレベルはこれ！',
          files: [file],
        });
      } catch (error) {
        console.error('シェアに失敗しました', error);
      }
    } else {
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
    <!-- 天気背景 -->
<div class="weather-background">

<!-- 晴れ -->
<img
  v-if="weatherType === 'sunny'"
  :src="sunnyImg"
  class="weather-sun"
/>

<!-- 曇り -->
<template v-if="weatherType === 'cloudy'">
  <img :src="cloudyImg" class="weather-cloud cloud1" />
  <img :src="cloudyImg" class="weather-cloud cloud2" />
</template>

<!-- 雨 -->
<template v-if="weatherType === 'rainy'">
  <div
    v-for="n in 30"
    :key="n"
    class="rain-drop"
    :style="{
      left: `${Math.random() * 100}%`,
      animationDelay: `${Math.random() * 2}s`,
      animationDuration: `${1 + Math.random()}s`
    }"
  >
    <img :src="raindropImg" />
  </div>
</template>

</div>
<!-- <div class="streak-badge"> -->
  <!-- レア率 {{ Math.floor(currentRareRate * 100) }}% -->
<!-- </div> -->

    <div class="roulette-wrapper">
      <svg class="progress-ring" viewBox="0 0 400 400">
        <circle class="progress-ring__background" r="180" cx="200" cy="200" />
        <circle
          class="progress-ring__circle"
          r="180" cx="200" cy="200"
          :style="progressBarStyle"
        />
      </svg>
      <div class="pointer">▼</div>

      <button @click="spin" class="gacha-button" :disabled="spinning">
        {{ spinning ? '抽選中...' : 'PUSH' }}
      </button>

      <div class="roulette-wheel" :style="{ transform: `rotate(${rotation}deg)` }">
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

      <!-- ① お化けクリック用（ランダム挨拶の適用 ＋ 3秒表示の維持アニメーション） -->
   <div 
  v-if="showGhost && !spinning && !exerciseResult" 
  class="pressure-ghost-fixed" 
  :class="{ 'is-fading': isGhostFading }" 
  @click="handleGhostClick" 
>
  <img src="@/assets/logo/ghost.png" alt="Ghost" class="ghost-img-mini" />
  
  <div class="char-speech-mini">
    {{ charSpeechText }}
  </div>
</div>

<!-- ② 待機時間を経て画面上に移動するキャラクタークリック用（フェードアウトのみ） -->
<div 
  v-if="!spinning && !exerciseResult"
  class="char-actor"
  :class="[charState, { 'is-fading': isClicked }]"
  @click="handleCharClick" 
>
  <img src="@/assets/logo/ghost.png" alt="Ghost" class="char-img" />
  
  <div v-if="charState === 'finished'" class="char-speech">押す？押さない？</div>
</div>

      <Transition name="fade-scale">
        <div v-if="exerciseResult && !spinning" class="result-overlay">
          <div id="share-area" class="result-card">
            <div class="level-badge">Lv.{{ exerciseResult.level }}</div>
            <h3>本日のメニュー</h3>
            <div class="exercise-text">{{ exerciseResult.text }}</div>
            <div class="result-actions">
              <button @click="shareResult" class="share-button">📱 シェア</button>
              <button @click="exerciseResult = null" class="close-button">OK!</button>
            </div>
          </div>
        </div>
      </Transition>


<!-- stamp -->
<Transition name="fade">
        <div v-if="showStampCard" class="modal-overlay" @click="closeStampCard">
          <div class="stamp-card-wrapper" @click.stop>
            <StampCard />
            <button @click="closeStampCard" class="close-btn">とじる</button>
          </div>
        </div>
      </Transition>

    </div>

    <!-- TEST WEATHER -->
     <!-- 
<div class="weather-debug"> 
 <button @click="weatherType = 'sunny'">☀ 晴れ</button> 
 <button @click="weatherType = 'cloudy'">☁ 曇り</button>
  <button @click="weatherType = 'rainy'">☂ 雨</button> 
 </div>
-->
  </div>
</template>

<style scoped>
.gacha-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-bottom: 20px;
  min-height: calc(100vh - 60px); /* ヘッダー分を引いた画面全体に背景色を適用 */
  background-color: #FFFDE7;     /* 白い隙間を埋めるためここに背景色を指定 */
  margin-top: 0;                 /* 上の余白を詰める */
  padding-top: 20px;             /* 上部にパディングを入れて位置を調整 */
}

.roulette-wrapper {
  position: relative;
  width: 300px;
  height: 300px;

  margin: 120px auto 60px auto;

  max-width: 90vw;
}

.roulette-wheel {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  position: relative;
  transition: transform 2s cubic-bezier(0.15, 0, 0.15, 1);
  border: 4px solid #2D3436;
  box-shadow: 4px 4px 0px #2D3436;
  overflow: hidden;
  z-index: 20;

  background: conic-gradient(
    from -36deg,
    #FF6B6B 0deg 72deg,
    #4ECDC4 72deg 144deg,
    #FFD93D 144deg 216deg,
    #6C5CE7 216deg 288deg,
    #FF85A2 288deg 360deg
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

.symbol {
  font-size: 38px;
  display: inline-block;
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
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(4px);
  border-radius: 50%;
}

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

.stamp-card-overlay {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  z-index: 150;
  display: flex;
  justify-content: center;
}

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

.stamp-grid {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  margin-top: 25px;
}

.stamp-slot {
  position: relative;
  width: 28px !important;  
  height: 28px !important;
  
  border-radius: 50%;
  background: #333 !important;
  border: 1px solid #555 !important;
  flex-shrink: 0;

  display: block !important;
}

.cell-img {
  position: absolute !important;
  width: 44px !important;
  height: 44px !important;
  
  top: 50% !important;
  left: 53% !important;
  transform: translate(-50%, -45%) !important;
  
  object-fit: contain;
  margin: 0 !important;
  padding: 0 !important;
  display: block !important;
}

.cell-img.large  { z-index: 1; }
.cell-img.medium { z-index: 2; }
.cell-img.small  { z-index: 3; }

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

.fade-slide-enter-active, .fade-slide-leave-active {
  transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translate(-50%, 20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translate(-50%, -10px) scale(0.9);
}

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

.streak-badge {
  background: #FFD93D;
  z-index: 100;
  color: #2D3436;
  border: 2px solid #2D3436;
  padding: 6px 16px;
  border-radius: 20px;
  font-weight: 900;
  font-size: 13px;
  margin-bottom: 24px;
  box-shadow: 3px 3px 0px #2D3436;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

.char-actor {
  position: absolute;
  top: 50%;
  left: -60vw; 
  transform: translateY(-50%);
  z-index: 35;
  width: 70px;
  height: auto;
  opacity: 0;
  cursor: pointer;
}

.char-img {
  width: 120%;
  height: auto;
  display: block;
  /* filter: hue-rotate(90deg) brightness(1.2) saturate(1.5); */
}

.char-actor.moving {
  opacity: 1;
  animation: moveInFromFarLeft 5s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

.char-actor.jumping {
  opacity: 1;
  left: 50%; 
  z-index: 41; 
  transform: translate(-50%, 110px);
  animation: jumpThreeTimes 3s ease-in-out forwards;
}

.char-actor.climbing {
  opacity: 1;
  left: 50%;
  z-index: 16;
  animation: climbToBackDiagonal 1s ease-in-out forwards;
}

.char-actor.finished {
  opacity: 1;
  left: 50%;
  z-index: 16;
  transform: translate(calc(-50% - 120px), -145px) rotate(-30deg);
  animation: breatheDiagonal 2s infinite alternate;
}

.char-speech {
  position: absolute;
  top: -35px;
  left: 50%;
  transform: translateX(-50%) rotate(30deg);
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

@keyframes moveInFromFarLeft {
  0% { 
    left: -80vw;
    transform: translate(0, 110px); 
  }
  100% { 
    left: 50%;
    transform: translate(-50%, 110px);
  }
}

@keyframes jumpThreeTimes {
  0%, 33.3%, 66.6%, 100% { transform: translate(-50%, 110px); }
  16.6%, 50%, 83.3% { transform: translate(-50%, 40px); }
}

@keyframes climbToBackDiagonal {
  0% { transform: translate(-50%, 110px) rotate(0deg); }
  100% { transform: translate(calc(-50% - 120px), -145px) rotate(-30deg); }
}

@keyframes breatheDiagonal {
  from { transform: translate(calc(-50% - 120px), -145px) rotate(-30deg) scale(1); }
  to { transform: translate(calc(-50% - 120px), -143px) rotate(-30deg) scale(1.03); }
}

.char-actor.is-fading {
  transition: opacity 3s ease-out, transform 3s ease-out !important;
  opacity: 0 !important;
  transform: translate(calc(-50% - 120px), -180px) scale(1.5) !important;
  pointer-events: none;
}

.char-actor:not(.is-fading) {
  cursor: pointer;
}


.ghost-img-mini {
  width: 150%;
  /* filter: hue-rotate(90deg) brightness(1.2); */
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
  z-index: 51; /* 念のため吹き出しをさらにお化けの画像より手前にする */
}

/* ★追加：お化けと吹き出しのフェードイン・アウト用トランジション ★ */
.fade-ghost-enter-active,
.fade-ghost-leave-active {
  transition: opacity 0.5s ease, transform 0.5s ease;
}

.fade-ghost-enter-from,
.fade-ghost-leave-to {
  opacity: 0;
  transform: translateY(10px); /* 少し下に沈みながらふわっと消える */
}

.pressure-ghost-fixed {
  position: absolute;
  right: -60px; 
  bottom: -70px;
  width: 50px;
  z-index: 50;
  opacity: 0.8;
  cursor: pointer;
  /* これを追加すると描画が安定します */
  will-change: transform, opacity;
  transform: translateZ(0); 

  transition: opacity 0.8s cubic-bezier(0.4, 0, 0.2, 1), 
              transform 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
  animation: pressureSwing 3s infinite ease-in-out;
}
.pressure-ghost-fixed.is-fading {
  opacity: 0 !important;
  /* 上に浮き上がりつつ、少し小さくなりながら回転して消える */
  transform: translateY(-40px) scale(0.8) rotate(15deg) !important;
  pointer-events: none;
}

@keyframes pressureSwing {
  0% { 
    transform: translateX(-3px) rotate(-5deg); 
  }
  50% { 
    transform: translateX(3px) rotate(5deg); 
  }
  100% { 
    transform: translateX(-3px) rotate(-5deg); 
  }
}


.progress-ring {
  position: absolute;
  width: 400px;
  height: 400px;
  top: 0;
  left: 0;
  margin-top: -44px;
  margin-left: -44px;
  transform: rotate(-90deg);
  display: block;
  z-index: 15;
  pointer-events: none;
  overflow: visible; 
}

.progress-ring__background {
  stroke: #2D3436 !important; 
  stroke-width: 4;
  fill: transparent;
}

.progress-ring__circle {
  transform: translate(0.5px, 0.5px);
  stroke: #FF00FF !important; 
  stroke-width: 10;
  stroke-linecap: round;
  fill: transparent;
  transition: stroke-dashoffset 0.8s ease-in-out;
}

/* stamp */
/* モーダル表示時のスタイル */
.modal-overlay {
  position: fixed; 
  top: 0; 
  left: 0; 
  width: 100%; 
  height: 100%;
  background: rgba(0, 0, 0, 0.7); 
  display: flex; 
  justify-content: center; 
  align-items: center; 
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.stamp-card-wrapper {
  display: flex; 
  flex-direction: column; 
  align-items: center; 
  gap: 15px;
  width: 90%; 
  max-width: 400px;
}

.close-btn {
  padding: 12px 20px; 
  border-radius: 15px; 
  border: 3px solid #2D3436;
  font-weight: 900; 
  cursor: pointer; 
  width: 100%; 
  background: #2D3436; 
  color: white;
  box-shadow: 4px 4px 0px rgba(0, 0, 0, 0.2);
}

/* トランジション（アニメーション）設定 */
.fade-enter-active, .fade-leave-active { 
  transition: opacity 0.3s; 
}
.fade-enter-from, .fade-leave-to { 
  opacity: 0; 
}
/* TENKI */
.weather-background {
  position: fixed;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  z-index: 1;
}


/* 晴れ */

.weather-sun {
  position: absolute;

  top: 80px;
  left: 120px;   /* ← right をやめて left */

  width: 190px; /* ← 少し大きく */

  opacity: 0.7; /* ← 背景らしさ */

  filter:
    drop-shadow(0 0 30px rgba(236, 185, 77, 0.45))
    brightness(1.08)
    saturate(1.1);

  animation: sunFloat 6s ease-in-out infinite;
}

/* 曇り */

.weather-cloud {
  position: absolute;
  width: 230px;

}

.cloud1 {
  top: 60px;
  left: -40px;

  animation: cloudMove1 20s linear infinite;
}

.cloud2 {
  top: 180px;
  right: -50px;

  animation: cloudMove2 25s linear infinite;
}

/* 雨 */

.rain-drop {
  position: absolute;
  top: -100px;

  animation-name: rainFall;
  animation-timing-function: linear;
  animation-iteration-count: infinite;
}

.rain-drop img {
  width: 18px;
  opacity: 0.35;
}

/* アニメ */

@keyframes rainFall {
  from {
    transform: translateY(0);
  }

  to {
    transform: translateY(120vh);
  }
}

@keyframes cloudMove1 {
  from {
    transform: translateX(0);
  }

  to {
    transform: translateX(120vw);
  }
}

@keyframes cloudMove2 {
  from {
    transform: translateX(0);
  }

  to {
    transform: translateX(-120vw);
  }
}

@keyframes sunFloat {
  0% {
    transform: translateY(0px) rotate(0deg);
  }

  50% {
    transform: translateY(10px) rotate(5deg);
  }

  100% {
    transform: translateY(0px) rotate(0deg);
  }
}

/* デバッグ */
.weather-debug {
  position: fixed;
  top: 10px;
  right: 10px;
  z-index: 9999;

  display: flex;
  gap: 8px;
}

.weather-debug button {
  border: 2px solid #2D3436;
  background: white;
  border-radius: 10px;
  padding: 6px 10px;
  font-weight: bold;
  cursor: pointer;

  box-shadow: 2px 2px 0 #2D3436;
}
</style>
