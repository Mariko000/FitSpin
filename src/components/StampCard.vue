<script setup>
// ここはボタンを表示して、クリックされたらストアの関数を呼ぶだけの「見た目（UI）」
import { ref,computed } from 'vue'
import { useExerciseStore } from '../stores/useExerciseStore'
import { holidayMaster } from '../data/holidayMaster.js'

// 画像アセットの読み込み
import circleSmall from '../assets/images/badges/cell-circle_small.png'
import circleMedium from '../assets/images/badges/cell-circle_medium.png'
import circleLarge from '../assets/images/badges/cell-circle_large.png'

const store = useExerciseStore()

// ★追加：表示中のシート番号（最初は現在の進捗シートを表示）
const viewingSheetIndex = ref(store.currentSheetIndex)

const recentStamps = computed(() => store.recentStamps || [])
const dailyCount = computed(() => store.dailyCount || 0)

// 現在のシート番号の計算
const currentSheetIndex = computed(() => {
  return store.currentSheetIndex
})

// 現在のシートに表示する7日分のスタンプデータの切り出し
const currentSheetStamps = computed(() => {
  const startIdx = (viewingSheetIndex.value - 1) * 7
  return store.stamps.slice(startIdx, startIdx + 7)
})

// ★修正：タイトルとステッカー情報の取得も viewingSheetIndex を使う
const sheetInfo = computed(() => {
  return store.getStickerInfoBySheet(viewingSheetIndex.value)
})

// ページを切り替える関数
const changeSheet = (index) => {
  viewingSheetIndex.value = index
}

/*
通常ダウンロード用：store.downloadSticker()
1週間連続で運動した時に、画面に現れるボタンから呼ぶ関数


テスト用：forceDownloadTest()
開発中にいつでもテストできる、赤いパネルのボタンから呼ぶ関数

2つの関数にそれぞれ演出を合流させる、
*/ 



//  【お祝い演出の司令塔】
const currentEffectState = ref('none')
const celebrationAsset = ref('')
const celebrationMessage = ref('')

// この関数が、画面をブルブル・爆発させながら、裏でストアのダウンロードを呼び出します
const startCelebrationEffect = async (sheetId, achievedDate) => {
  const todayJST = store.getTodayJST()
  const dateKey = todayJST.slice(5)
  const matchedHoliday = holidayMaster[dateKey]

  celebrationAsset.value = matchedHoliday?.asset || sheetInfo.value.asset
  celebrationMessage.value = matchedHoliday?.message || sheetInfo.value.achievedMessage

  currentEffectState.value = 'shaking'

  // 1. 暗転と同時に「大きなデコレーション（出現）」
  setTimeout(() => {
    currentEffectState.value = 'celebrating'
  }, 500)

  // 2. その0.3秒後（合計0.8秒後）に「弾ける（バースト）」
  setTimeout(() => {
    // 💡 裏でダウンロード実行
    store.downloadSticker(sheetId, achievedDate)
  }, 800)

  // 4.5秒後に終了
  setTimeout(() => {
    currentEffectState.value = 'none'
  }, 4500)
}

// 【合流ルート①：テスト用】
// 元からあった forceDownloadTest も、アラートを出すのをやめて、上の「演出の司令塔」に直接合流させる！
const forceDownloadTest = (weekNum) => {
  const ids = ['week1', 'week2', 'week3', 'month1']
  const targetId = ids[weekNum - 1]
  
  // 💡 ストアの getTodayJST() から作った、Macの日付と連動した正しい日付文字列を渡す！
  // これにより、Macを土日に変えた設定がそのままダウンロード処理まで引き継がれます
  const todayJST = store.getTodayJST() // 例: "2026-05-23"
  const formattedDate = todayJST.replace(/-/g, '.') // 表示用に "." に変換するだけ

  // 司令塔を呼び出す！
  startCelebrationEffect(targetId, formattedDate)
}


</script>

<template>
<div class="stamp-card">
  
  <div class="sheet-tabs" style="display: flex; justify-content: center; gap: 5px; margin-bottom: 15px;">
    <button 
      v-for="i in 4" :key="i" 
      @click="changeSheet(i)"
      :style="{
        padding: '4px 8px',
        fontSize: '11px',
        borderRadius: '5px',
        border: '2px solid #2D3436',
        backgroundColor: viewingSheetIndex === i ? '#6C5CE7' : '#fff',
        color: viewingSheetIndex === i ? '#fff' : '#2D3436',
        fontWeight: 'bold',
        cursor: 'pointer'
      }"
    >
      {{ i }}週目
    </button>
  </div>

  <div class="stamp-header">
    <h3>{{ sheetInfo.title }}</h3>
    <div class="count-viewer">Today: {{ dailyCount }} / 3</div>
  </div>
    
    <div class="stamp-grid">
  <div v-for="n in 7" :key="n" class="stamp-slot">
    
    <div v-if="currentSheetStamps[n-1]" class="stamp-content is-stamped">
      <img :src="circleLarge"  class="cell-img large" v-if="currentSheetStamps[n-1].count >= 3" />
      <img :src="circleMedium" class="cell-img medium" v-if="currentSheetStamps[n-1].count >= 2" />
      <img :src="circleSmall"  class="cell-img small" v-if="currentSheetStamps[n-1].count >= 1" />
    </div>
    
    <span v-else class="empty-slot">{{ n }}</span>
  </div>
</div>
<!-- ステッカー表示エリアの条件分岐とテキスト表示部分をストアのgetStickerInfoBySheetから参照 -->
<div v-if="store.stamps.length >= sheetInfo.needed" class="sticker-present-area" style="margin-top: 15px; border-top: 1px solid #ddd; padding-top: 12px; text-align: center;">
  
  <p style="font-size: 13px; color: #333; margin-bottom: 8px;">
    {{ store.stamps.length === sheetInfo.needed ? sheetInfo.achievedMessage : sheetInfo.normalMessage }}
  </p>

  <div style="display: flex; justify-content: center; align-items: center; gap: 10px;">
    <img 
      :src="sheetInfo.asset" 
      alt="Sticker" 
      style="width: 50px; height: 50px; object-fit: contain;" 
    />
    <!-- ※ store.stickers[sheetInfo.id]?.date と指定することで、
      すでに存在している獲得日、もしくは今日の日付文字列をdownloaded: true のフラグが立った状態で確実にストアへ渡せる -->
      <button 
        @click="startCelebrationEffect(sheetInfo.id, store.stickers[sheetInfo.id]?.date || new Date().toLocaleDateString('ja-JP').replace(/\//g, '.'))"
        style="padding: 6px 12px; background-color: #6C5CE7; color: white; border: none; border-radius: 8px; font-size: 12px; cursor: pointer; font-weight: bold;"
      >
        ステッカーをダウンロード
      </button>
    </div>
  </div>

<!-- v-if="false"にする -->
<!--    <div v-if="true" class="test-panel" style="margin-top: 20px; padding: 10px; border: 2px dashed #ff4757; border-radius: 10px; background: #fff5f5;">
  <p style="font-size: 10px; color: #ff4757; font-weight: bold; margin-bottom: 5px;">⚠️ 緊急テスト用：強制ダウンロード済み処理</p>
  <div style="display: flex; flex-wrap: wrap; gap: 5px;">
    <button 
      v-for="i in 4" :key="'test-'+i"
      @click="forceDownloadTest(i)" style="padding: 4px 8px; font-size: 10px; background: #ff4757; color: white; border: none; border-radius: 4px; cursor: pointer;"
    >
      {{ i }}週目 強制クリア
    </button>
  </div>
</div>
-->


<div v-if="currentEffectState === 'celebrating'" class="celebration-overlay">
    
    <div class="celebration-message-area">
      <p class="celebration-white-text">{{ celebrationMessage }}</p>
    </div>

    <div class="celebration-character">
      <img :src="celebrationAsset" alt="Celebrating Spimaru" class="spimaru-bounce" />
    </div>

    <div class="confetti-container">
      <div v-for="i in 24" :key="i" :class="'confetti-piece piece-' + i"></div>
    </div>

</div>

  
  </div> 
  </template>
   
 

<style scoped>
.stamp-card {
  width: 100%;
  max-width: 400px;
  background: #ffffff;
  padding: 24px;
  border-radius: 20px;
  border: 4px solid #2D3436;
  box-shadow: 8px 8px 0px #2D3436;
  margin: 0 auto;
}

.stamp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.stamp-content {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
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

.congrats-msg {
  font-size: 13px;
  font-weight: 900;
  color: #6C5CE7;
  margin-top: 20px;
}

.count-viewer {
  color: #6C5CE7;
  font-weight: 900;
  font-size: 14px;
}

.close-btn {
  padding: 10px 20px; border-radius: 15px; border: 3px solid #2D3436;
  font-weight: 900; cursor: pointer; width: 100%; background: #2D3436; color: white;
  box-shadow: 4px 4px 0px rgba(0, 0, 0, 0.2);
}

/* 
   お祝い演出のメッセージエリア 
   （カード中央の黒いモヤの中に綺麗に収めます）
*/
/*
ボタンを押した瞬間、スタンプカードそのものが「ブルブルッ」と小さく震えたあと、カード全体からブワッと紙吹雪（クラッカーを鳴らしたようなエフェクト）が飛び散る
＋
カードの背景が少し暗くなり、中央に
スピまるが現れてきて
スピまるのイラストのすぐ下に、吹き出しのようなデザインでメッセージが「カタカタカタ…」とタイピング風に表示される
*/
/* --- 1. カード全体のブルブル（シェイク）効果 --- */
.stamp-card.is-shaking {
  animation: cardShake 0.1s linear infinite;
}



/* --- 4. 主役スピまるのピョコン！バウンドアニメーション --- */
.celebration-character {
  width: 140px;
  height: 140px;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 110;
  margin-bottom: 10px;
}

.celebration-character img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.spimaru-bounce {
  /* 0.3秒遅れで下からポップアップしてきて、その後は楽しくフカフカ縦揺れする */
  animation: 
    popInCharacter 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) 0.3s forwards,
    gentleBounce 0.6s ease-in-out infinite alternate 0.8s;
  transform: scale(0); /* 最初は隠しておく */
}

@keyframes popInCharacter {
  from { transform: scale(0) translateY(50px); }
  to { transform: scale(1) translateY(0); }
}

@keyframes gentleBounce {
  from { transform: translateY(0); }
  to { transform: translateY(-10px); }
}



/* --- 5. メッセージ配置エリア（スピまるのすぐ下、カード内に収める） --- */
.celebration-message-area {
  position: relative; 
  margin-top: 15px;
  width: 90%;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 110;
}

@keyframes fadeInWhiteText {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* --- 6. 映画風・真っ白な極太メッセージテキスト --- */
.celebration-white-text {
  font-size: 21px !important;       /* 大きめの文字サイズ */
  font-weight: 900 !important;      /* 超極太 */
  color: #FFFFFF !important;        /* 真っ白 */
  line-height: 1.4;
  margin: 0;
  text-align: center;
  white-space: pre-wrap;
  display: block !important;
  max-width: 100% !important;
  opacity: 0;
  
  /* 輪郭をクッキリさせる黒シャドウ */
  text-shadow: 
    2px 2px 0px #000, -2px -2px 0px #000,
    2px -2px 0px #000, -2px 2px 0px #000,
    0px 4px 8px rgba(0, 0, 0, 0.8);

  /* 暗転の0.5秒後に、ポップコーンのようにポンッと弾けて現れる */
  animation: popcornPopIn 0.4s cubic-bezier(0.175, 0.885, 0.42, 1.4) 0.5s forwards;
}

@keyframes popcornPopIn {
  0% { transform: scale(0.5); opacity: 0; }
  70% { transform: scale(1.15); opacity: 1; } /* 一度少し大きめに膨らむ */
  100% { transform: scale(1); opacity: 1; }    /* 通常サイズに着地 */
}


@keyframes cardShake {
  0% { transform: translate(2px, 1px) rotate(0deg); }
  10% { transform: translate(-1px, -2px) rotate(-1deg); }
  20% { transform: translate(-3px, 0px) rotate(1deg); }
  30% { transform: translate(0px, 2px) rotate(0deg); }
  40% { transform: translate(1px, -1px) rotate(1deg); }
  50% { transform: translate(-1px, 2px) rotate(-1deg); }
  60% { transform: translate(-3px, 1px) rotate(0deg); }
  70% { transform: translate(2px, 1px) rotate(-1deg); }
  80% { transform: translate(-1px, -1px) rotate(1deg); }
  90% { transform: translate(2px, 2px) rotate(0deg); }
  100% { transform: translate(1px, -2px) rotate(-1deg); }
}

/* --- 2. 画面を暗くする映画館風の暗転背景 --- */
.celebration-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 16px;
  background: rgba(0, 0, 0, 0.75); /* 💡 少し暗めの黒スケルトンで主役を引き立てる */
  z-index: 100;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  animation: fadeInOverlay 0.3s ease-out forwards;
}

@keyframes fadeInOverlay {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* --- 7. 前面で大爆発する紙吹雪・リボン（24個分に増量・ランダム化） --- */
.confetti-container {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  pointer-events: none;
  z-index: 120; /* 最前面 */
  perspective: 1000px; /* 3D的な回転のための奥行き */
}

/* 紙吹雪の一粒一粒の共通設定 */
.confetti-piece {
  position: absolute;
  top: 40%;  /* スピまるの少し上から爆発 */
  left: 50%;
  opacity: 0;
  transform-style: preserve-3d;
}

/* 🎨 キラキラの見た目設定（サイズを少し拡大、リボンを長めに） */
/* 丸粒 */
.confetti-piece.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}
/* リボン（細長） */
.confetti-piece.ribbon {
  width: 18px;
  height: 6px;
  border-radius: 2px;
}

/* 丸粒とリボン（長方形）を織り交ぜた24個のキラキラ */
/* 🎨 キラキラの見た目設定：サイズをひと回り大きく、リボンを太く変更 */
.piece-1  { width: 15px; height: 15px; border-radius: 50%; background: #ff4757; animation: exp-1 2.0s cubic-bezier(0.1, 0.8, 0.3, 1) forwards; }
.piece-2  { width: 22px; height: 10px; border-radius: 2px; background: #2ed573; animation: exp-2 2.3s cubic-bezier(0.1, 0.8, 0.3, 1) forwards; }
.piece-3  { width: 14px; height: 14px; border-radius: 50%; background: #1e90ff; animation: exp-3 1.9s cubic-bezier(0.1, 0.8, 0.3, 1) forwards; }
.piece-4  { width: 24px; height: 9px;  border-radius: 2px; background: #ffa502; animation: exp-4 2.2s cubic-bezier(0.1, 0.8, 0.3, 1) forwards; }
.piece-5  { width: 16px; height: 16px; border-radius: 50%; background: #ff6b81; animation: exp-5 2.4s cubic-bezier(0.1, 0.8, 0.3, 1) forwards; }
.piece-6  { width: 20px; height: 10px; border-radius: 2px; background: #70a1ff; animation: exp-6 2.1s cubic-bezier(0.1, 0.8, 0.3, 1) forwards; }
.piece-7  { width: 13px; height: 13px; border-radius: 50%; background: #7bed9f; animation: exp-7 2.3s cubic-bezier(0.1, 0.8, 0.3, 1) forwards; }
.piece-8  { width: 18px; height: 9px;  border-radius: 2px; background: #eccc68; animation: exp-8 2.0s cubic-bezier(0.1, 0.8, 0.3, 1) forwards; }
.piece-9  { width: 22px; height: 10px; border-radius: 2px; background: #ff4757; animation: exp-3 2.2s cubic-bezier(0.1, 0.8, 0.3, 1) forwards; }
.piece-10 { width: 15px; height: 15px; border-radius: 50%; background: #2ed573; animation: exp-5 1.9s cubic-bezier(0.1, 0.8, 0.3, 1) forwards; }
.piece-11 { width: 24px; height: 9px;  border-radius: 2px; background: #1e90ff; animation: exp-1 2.5s cubic-bezier(0.1, 0.8, 0.3, 1) forwards; }
.piece-12 { width: 16px; height: 16px; border-radius: 50%; background: #ffa502; animation: exp-7 2.1s cubic-bezier(0.1, 0.8, 0.3, 1) forwards; }
.piece-13 { width: 20px; height: 10px; border-radius: 2px; background: #ff6b81; animation: exp-8 2.0s cubic-bezier(0.1, 0.8, 0.3, 1) forwards; }
.piece-14 { width: 14px; height: 14px; border-radius: 50%; background: #70a1ff; animation: exp-2 2.2s cubic-bezier(0.1, 0.8, 0.3, 1) forwards; }
.piece-15 { width: 22px; height: 9px;  border-radius: 2px; background: #7bed9f; animation: exp-4 2.4s cubic-bezier(0.1, 0.8, 0.3, 1) forwards; }
.piece-16 { width: 13px; height: 13px; border-radius: 50%; background: #eccc68; animation: exp-6 1.8s cubic-bezier(0.1, 0.8, 0.3, 1) forwards; }
.piece-17 { width: 15px; height: 15px; border-radius: 50%; background: #ff4757; animation: exp-6 2.1s cubic-bezier(0.1, 0.8, 0.3, 1) forwards; }
.piece-18 { width: 24px; height: 10px; border-radius: 2px; background: #2ed573; animation: exp-4 2.5s cubic-bezier(0.1, 0.8, 0.3, 1) forwards; }
.piece-19 { width: 14px; height: 14px; border-radius: 50%; background: #1e90ff; animation: exp-8 2.0s cubic-bezier(0.1, 0.8, 0.3, 1) forwards; }
.piece-20 { width: 22px; height: 9px;  border-radius: 2px; background: #ffa502; animation: exp-2 2.3s cubic-bezier(0.1, 0.8, 0.3, 1) forwards; }
.piece-21 { width: 16px; height: 16px; border-radius: 50%; background: #ff6b81; animation: exp-7 2.2s cubic-bezier(0.1, 0.8, 0.3, 1) forwards; }
.piece-22 { width: 20px; height: 10px; border-radius: 2px; background: #70a1ff; animation: exp-1 1.9s cubic-bezier(0.1, 0.8, 0.3, 1) forwards; }
.piece-23 { width: 15px; height: 15px; border-radius: 50%; background: #7bed9f; animation: exp-5 2.1s cubic-bezier(0.1, 0.8, 0.3, 1) forwards; }
.piece-24 { width: 24px; height: 9px;  border-radius: 2px; background: #eccc68; animation: exp-3 2.4s cubic-bezier(0.1, 0.8, 0.3, 1) forwards; }

/* 🚀 飛散距離を約1.8倍に拡張。画面の端までランダムに激しく弾け飛ばす（回転数も増量） */
@keyframes exp-1 { 0% { transform: translate(0, 0) scale(1) rotate(0deg); opacity: 1; } 100% { transform: translate(-240px, -280px) scale(0.6) rotate(1080deg); opacity: 0; } }
@keyframes exp-2 { 0% { transform: translate(0, 0) scale(1) rotate(0deg); opacity: 1; } 100% { transform: translate(260px, -250px) scale(0.7) rotate(-720deg); opacity: 0; } }
@keyframes exp-3 { 0% { transform: translate(0, 0) scale(1) rotate(0deg); opacity: 1; } 100% { transform: translate(-280px, 60px) scale(0.6) rotate(1440deg); opacity: 0; } }
@keyframes exp-4 { 0% { transform: translate(0, 0) scale(1) rotate(0deg); opacity: 1; } 100% { transform: translate(290px, 90px) scale(0.7) rotate(-1080deg); opacity: 0; } }
@keyframes exp-5 { 0% { transform: translate(0, 0) scale(1) rotate(0deg); opacity: 1; } 100% { transform: translate(-120px, -320px) scale(0.6) rotate(1080deg); opacity: 0; } }
@keyframes exp-6 { 0% { transform: translate(0, 0) scale(1) rotate(0deg); opacity: 1; } 100% { transform: translate(140px, -330px) scale(0.7) rotate(-1440deg); opacity: 0; } }
@keyframes exp-7 { 0% { transform: translate(0, 0) scale(1) rotate(0deg); opacity: 1; } 100% { transform: translate(-150px, 280px) scale(0.6) rotate(720deg); opacity: 0; } }
@keyframes exp-8 { 0% { transform: translate(0, 0) scale(1) rotate(0deg); opacity: 1; } 100% { transform: translate(160px, 270px) scale(0.7) rotate(-1080deg); opacity: 0; } }


</style>