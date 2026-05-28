<script setup>
import { ref, onMounted, computed } from 'vue'
import { useExerciseStore } from '../stores/useExerciseStore'
import { stickerMaster } from '@/data/stickerMaster.js'
import { holidayMaster } from '@/data/holidayMaster.js'

const store = useExerciseStore()

// ★ ここで shelf.svg をインポート
import shelfSvg from '../assets/logo/shelf.png'



// ページ表示時に扉を開ける演出

const isOpen = ref(false)

onMounted(() => {
  // ★ ここを追加：画面を開いた時に未獲得のステッカーがないかチェック
  store.checkStickerAward();

  setTimeout(() => {
    isOpen.value = true
  }, 300)
})


// マスタのキー（week1, week2等）を確実にオブジェクトの id に紐付けて配列化する
// 今後は辞書に追加するだけで自動で棚に並びます！
// 画像（asset）が登録されているアイテムだけを厳選して棚に並べる
const collectionItems = computed(() => {
  // 1. まず通常のマスタ（1週間〜1ヶ月）を配列化
  const items = Object.entries(stickerMaster).map(([key, value]) => ({
    ...value,
    id: key
  }))

  // 2. holidayMaster の中から、ちゃんと画像パス（asset）が登録されているものだけを合流させる
  Object.entries(holidayMaster).forEach(([key, value]) => {
    if (value.asset) { // 💡 ここ！画像パスが書いてある場合だけ棚に追加する！
      items.push({
        ...value,
        id: key
      })
    }
  })

  return items
})
</script>

<template>
  <div class="cabinet-wrapper">
  <div class="collection-room" :class="{ 'is-open': isOpen }">
    
    <div class="door-left"></div>
    <div class="door-right"></div>

    <div class="room-content">
      <h2 class="collection-title"></h2>
      
      <div class="shelf-display" :style="{ backgroundImage: `url(${shelfSvg})` }">
        <div class="sticker-grid">
          <div v-for="item in collectionItems" :key="item.id" class="sticker-item">
<!-- store.stickers[item.id] の後ろに ?（オプショナルチェイニング） を付けることで、
  データがまだ存在しなくてもエラーを出さずに安全にスキップ（または else 側の未獲得表示）させる -->
            <div v-if="store.stickers[item.id]?.downloaded" class="sticker-wrapper achieved">
              <img :src="item.asset" :alt="item.title" />
              <p class="date">{{ store.stickers[item.id]?.date }} 獲得</p>
            </div>

            <div v-else class="sticker-wrapper locked">
              <div class="image-container">
                <img :src="item.asset" class="silhouette" />
                <span class="question-mark">?</span>
              </div>

              <p v-if="store.stickers[item.id]?.date" class="date">
                {{ store.stickers[item.id]?.date }}
              </p>
            </div>

            <p class="sticker-name">{{ item.title }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>

</div>
</template>

<style scoped>


/* --- 全体レイアウト --- */
.collection-room {
  width: 100%;
  position: relative;
  min-height: 100vh;
  background-color: #FFFDE7;
  overflow: hidden;
  display: flex;
  flex-direction: column; /* タイトルと棚を縦に並べる */
  align-items: center;
  padding-top: 40px;
}
/* --- 🚪 扉のアニメーション --- */
.door-left, .door-right {
  position: absolute;
  top: 65px;
  /* ★ 高さを100%から下げた分だけ引く */
  height: calc(100% - 65px);
  width: 50%;
  height: 100%;
  z-index: 100;
  background: linear-gradient(90deg, #432c22, #352219); /* 重厚な暗い色 */
  transition: transform 1.2s cubic-bezier(0.4, 0, 0.2, 1);
}
.door-left { left: 0; border-right: 4px solid #000; }
.door-right { right: 0; border-left: 4px solid #000; }

/* オープン時の動き */
.collection-room.is-open .door-left { transform: translateX(-100%); }
.collection-room.is-open .door-right { transform: translateX(100%); }



/* --- シェルフ表示 --- */
/*  */
.shelf-display {
  /* 💡 125%だとはみ出す原因になるため、100%で画像全体をコンテナにフィットさせます */
  background-size: 100% 100%; 
  
  /* 💡 固定のpaddingではなく、横幅(100vw)に対する比率で上部余白を可変にします */
  padding-top: 16vw; 
  
  /* 💡 横幅を画面いっぱいにしつつ、PCでの最大幅を1000pxに制限 */
  width: 100vw;
  max-width: 1000px;
  
  /* 💡 高さを固定(px)ではなく、横幅に対する比率で自動追従させます（これで下部が白く余りません） */
  height: 98vw;
  max-height: 980px;
  
  background-repeat: no-repeat;
  background-position: center top;
  display: flex;
  justify-content: center;
}

.sticker-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  
  /* 💡 ここ！上部の余白を「5.5vw → 2vw」に小さくして全体を上に引き上げました */
  margin-top: 2vw; 

  /* 💡 縦横の比率はそのまま維持します */
  row-gap: 6.5vw;
  height: 54vw; 
  column-gap: 8vw; 
  width: 60%; 

  /* PC最大幅（1000px以上）のときも同様に上に引き上げます */
  @media (min-width: 1000px) {
    /* 💡 元の「55px → 20px」にしてPC表示時も上にずらします */
    margin-top: 20px;
    row-gap: 65px;
    height: 540px;
    column-gap: 80px;
  }
}

/* --- 🏆 ステッカーのサイズ --- */
/* --- 🏆 ステッカーのサイズ --- */
.sticker-wrapper img,
.image-container {
  /* 💡 スマホ・タブレット（1000px未満）の時は、一回り小さいサイズ（9.5vw）にします */
  width: 9.5vw;
  height: 9.5vw;
  
  /* PCサイズ（1000px以上）の時は、元の完璧な115pxをキープします */
  @media (min-width: 1000px) {
    width: 115px;
    height: 115px;
  }
  
  max-width: 115px;
  max-height: 115px;
}

/* 💡 追加：ステッカーが縮んだ分、名前（文字）が離れないように位置をキュッと上に寄せます */
.sticker-item {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  /* 縦の要素同士を上詰めで密着させる */
  gap: 2px; 
}

.sticker-wrapper img {
  display: block;
}
.achieved img {
  margin-bottom: -12px;
}

/* 文字と画像の隙間を詰める（gapの設定を確実に効かせる） */
.sticker-item, 
.sticker-item.achieved, 
.sticker-item.locked {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  gap: 2px; 
}

.date {
  font-size: 7px;
  font-weight: bold;
  color: #6C5CE7;

  margin: 2px 0 0 0;
  line-height: 1;

  transform: translateY(-6px);
}

.sticker-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.locked img.silhouette {
  width: 100%;
  height: 100%;
  object-fit: contain;

  filter:
    brightness(0)
    invert(1)
    contrast(100)
    brightness(2);

  opacity: 1;
}

.image-container {
  position: relative;
}

/* 「？」マークは、白いシルエットの中で見えるように「黒」にします */
/* 「？」マーク：白いシルエットの中で見えるように「黒」にする */
.question-mark {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  
  /* 💡 修正：スマホ・タブレット時は、親要素（image-container）の幅に対して自動縮小させます */
  font-size: 5vw; 
  
  font-weight: 900;
  color: #2D3436; 
  z-index: 2;
  pointer-events: none;
  
  /* 💡 追加：PCサイズ（1000px以上）のときは、元の完璧な40pxに固定します */
  @media (min-width: 1000px) {
    font-size: 40px;
  }
}

/* 獲得済みのステッカー（カラー）はそのまま、棚から浮かせる影だけ維持 */
.achieved img {
  filter: drop-shadow(0px 8px 4px rgba(0,0,0,0.5));
}
/* --- タイトルを少し調整（棚に被らないように） --- */
.collection-title {
  font-size: 32px;
  font-weight: 900;
  margin-bottom: 20px;
  color: #2D3436;
  text-shadow: 2px 2px 0px #fff;
}

.date {
  font-size: 10px;
  font-weight: bold;
  color: #6C5CE7;
}

/* ステッカー名：シールのすぐ下に来るように */
.sticker-name {
  color: #FFFFFF;
  font-weight: bold;
  text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
  margin: 0; /* 余計なマージンを消す */
  line-height: 1.2;
}

</style>