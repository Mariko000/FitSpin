// import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { stickerMaster } from '@/data/stickerMaster.js'
import { holidayMaster } from '@/data/holidayMaster.js'
// 祝日の辞書

export const useExerciseStore = defineStore('exercise', {
  
  state: () => ({
    // 初期値はlocalStorageから取得
    stamps: JSON.parse(localStorage.getItem('stampHistory') || '[]'),

    dailyCount: parseInt(localStorage.getItem('dailyCount') || '0'),
    lastSpinDate: localStorage.getItem('lastSpinDate') || '',
    streakCount: parseInt(localStorage.getItem('streakCount') || '0'),
    // ★追加
  previousDailyCount: 0,

  // ★追加
  didDailyReset: false,
    symbols: ['✨', '⭐', '😊', '🕶️', '🌈'],

    // ★ 追加：ヘッダー・メイン間で共有するサウンド設定
    isMuted: false,
    volume: 0.5, // 初期値 50%


    // ★ステッカーを辞書から
    stickers: JSON.parse(localStorage.getItem('fitspin_stickers')) || {}
  }),


  getters: {
    // 直近7日分のスタンプ
    recentStamps: (state) => state.stamps.slice(-7),

    // 現在たまっているスタンプの総数から「どのシートの期間か」を判定
    currentSheetIndex(state) {
      const totalStamps = state.stamps.length;
      if (totalStamps < 7) return 1; // 1枚目のシート（1〜7日）
      if (totalStamps < 14) return 2; // 2枚目のシート（8〜14日）
      if (totalStamps < 21) return 3; // 3枚目のシート（15〜21日）
      return 4; // 4枚目（1ヶ月/22〜30日）
    },

    // ★ 追加：スタンプ帳が7日間分埋まっているか判定する Getter
    isOneWeekCompleted: (state) => {
      // 直近のスタンプ数が7日分あり、かつすべてが埋まっているか
      if (state.stamps.length < 7) return false;
      // 最近7日間のレコードがすべて存在するかチェック
      return state.stamps.slice(-7).length === 7;
    },
    getStickerInfoBySheet: (state) => (sheetIndex) => {
      const sticker = Object.values(stickerMaster)[sheetIndex - 1]
    
      if (!sticker) {
        return null
      }
    
      // 1〜4のインデックスから、共通のID（week1〜month1）を確定させる
      const ids = ['week1', 'week2', 'week3', 'month1'];
      const unifiedId = ids[sheetIndex - 1];
    
      return {
        ...sticker,
        id: unifiedId, // ★ここでIDを 'week1' 等に強制統一してVueに渡す
    
        achieved: !!state.stickers[unifiedId],
    
        downloaded:
          state.stickers[unifiedId]?.downloaded || false,
    
        date:
          state.stickers[unifiedId]?.date || null
      }
    },


    // 今日のレア判定確率の計算
    currentRareRate: (state) => {
      const baseRate = 0.2;
      const streakBonus = state.streakCount * 0.05;
      const effortBonus = state.dailyCount * 0.10;
      return Math.min(baseRate + streakBonus + effortBonus, 0.8);
    }
  },

  actions: {
    // 日跨ぎ専用の処理: 日付が変わった時のリセット＆継続カウントアップを一括で行う関数
    handleDailyReset(today) {
      console.log('🎉 日付変更を検知：データを更新します')
      
      // 1. 昨日の運動回数を退避し、今日の回数をゼロにする（ピンクの輪っかをリセット！）
      this.previousDailyCount = this.dailyCount
      this.dailyCount = 0

      // 2. 継続日数を安全にカウントアップする
      // （すでにスタンプ履歴があり、かつ前日などに運動していれば streakCount を進める）
      if (this.stamps.length > 0) {
        this.streakCount++
      } else {
        this.streakCount = 1
      }

      // 3. 日付を今日に更新し、演出フラグをONにしてセーブ
      this.lastSpinDate = today
      this.didDailyReset = true
      this.saveToLocalStorage()
    },
    initialize() {
      const today = this.getTodayJST()

      if (this.lastSpinDate !== today) {
        // 💡 共通のリセット処理を実行
        this.handleDailyReset(today)
      }
    },
    
      /* if (this.lastSpinDate !== today) {
        console.log('日付変更を検知')
    
        this.previousDailyCount = this.dailyCount
        this.dailyCount = 0
        
        // 💡 修正：前日にもちゃんと運動ログ（stamps）があれば、継続日数を増やす！
        if (this.stamps.length > 0) {
          this.streakCount++
        } else {
          this.streakCount = 1
        }
    
        this.lastSpinDate = today
        this.didDailyReset = true
    
        this.saveToLocalStorage()
      }
    },*/

    // アプリ起動時や画面遷移時に状態を最新にする
    // initialize() {
      // const getJstDateString = () => {
        // const now = new Date();
        // 9時間（32,400,000ミリ秒）を足してJSTに変換
        // const jstDate = new Date(now.getTime() + 32400000);
        // return jstDate.toISOString().split('T')[0];
      // };
      
      // const today = getJstDateString();
    // },

    // 日付取得
    getTodayJST() {
      const now = new Date()
      const jst = new Date(now.getTime() + 9 * 60 * 60 * 1000)
      return jst.toISOString().split('T')[0]
    },

    // 運動記録の追加（スタンプ更新）
// 運動記録の追加（スタンプ更新）
addExerciseRecord(result) {
  const today = this.getTodayJST()

      // 💡 ルーレットを回した瞬間にも日付チェックを行い、変わっていれば安全にリセット
      if (this.lastSpinDate !== today) {
        this.handleDailyReset(today)
      }

      // 運動回数を増やす（ここから下はピンクの輪っかが綺麗に塗られていきます！）
      this.dailyCount++

      // 対象の日のスタンプデータを検索
      let todayStamp = this.stamps.find(s => s.date === today)


  if (!todayStamp) {
    // 今日初めての運動の場合
    todayStamp = {
      date: today,
      level: result.level,
      symbol: this.symbols[result.level - 1],
      count: this.dailyCount,
      hasBadge: false,
      logs: [{
        level: result.level,
        text: result.text,
        time: new Date().toLocaleTimeString()
      }]
    }
    this.stamps.push(todayStamp)
  } else {
    // 2回目以降の運動の場合
    todayStamp.count = this.dailyCount
    todayStamp.level = result.level
    todayStamp.symbol = this.symbols[result.level - 1]

    if (!todayStamp.logs) {
      todayStamp.logs = []
    }

    // ログは上限なく必ず追加する
    todayStamp.logs.push({
      level: result.level,
      text: result.text,
      time: new Date().toLocaleTimeString()
    })
  }

  // スタンプとしての表示（バッジ）は3回以上でTrueにする
  if (this.dailyCount >= 3) {
    todayStamp.hasBadge = true
  }

  this.stamps = this.stamps.slice(-31)
  this.saveToLocalStorage()
  this.checkStickerAward()

  window.dispatchEvent(new Event('spin-updated'))
},


    // ステッカー獲得の判定処理
    checkStickerAward() {
      // 💡 7日目の3回目が押された瞬間（stamps.lengthが7になった時）に判定させたいので、ここをスタンプ総数にする
      const totalStamps = this.stamps.length
    
      let updated = false
      const ids = ['week1', 'week2', 'week3', 'month1'];
    
      Object.values(stickerMaster).forEach((sticker, index) => {
        const unifiedId = ids[index] || sticker.id;
        
        if (
          totalStamps >= sticker.needed && // 💡 ここを totalStamps に！
          !this.stickers[unifiedId]?.date
        ) {
          this.stickers[unifiedId] = {
            date: new Date()
              .toLocaleDateString('ja-JP')
              .replace(/\//g, '.'),
            downloaded: false,
          }
          updated = true
        }
      });
    
      if (updated) {
        this.stickers = { ...this.stickers }
        this.saveToLocalStorage()
      }
    },

// 画像合成・ダウンロードのロジック
async downloadSticker(stickerId, achievedDate) {
  // ★重要：ダウンロード直前に判定を走らせて、ステータスを確実に「獲得済み」に更新する
  this.checkStickerAward();

  // ------------ ここから祝日判定 ------------
  const todayJST = this.getTodayJST(); // 例: "2026-05-18" などの文字列が取れる
  const dateKey = todayJST.slice(5);  // 前の4桁年とハイフンを削って、後ろの "05-18" だけを切り出す

  console.log(`[祝日テスト] 今日の判定キー: ${dateKey}`);

  let matchedHoliday = holidayMaster[dateKey];

  // 祝日がなく、かつ今日が土日（0:日, 6:土）なら、辞書の 'weekend' を適用するロジック
  const nowJST = new Date();
  const dayOfWeek = nowJST.getDay();
  const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;

  if (!matchedHoliday && isWeekend) {
    matchedHoliday = holidayMaster['weekend']; 
  }

  if (matchedHoliday) {
    console.log(`🎉【祝日ヒット！】今日は「${matchedHoliday.name}」です！`);
    console.log(`👕 解放予定の衣装ID: ${matchedHoliday.costumeId}`);
    console.log(`💬 メッセージ: ${matchedHoliday.message}`);
  } else {
    console.log(`ℹ️ [祝日テスト] 今日は通常の獲得日です（該当する国際祝日はありません）。`);
  }
  // ------------ ここまで ------------

  // もし今日が祝日で、その祝日に特別な画像（asset）が登録されていればそれを使い、なければ通常のステッカー画像を使う！
  const imagePath = matchedHoliday?.asset || stickerMaster[stickerId]?.asset;
  
  const canvas = document.createElement('canvas');
  canvas.width = 500;
  canvas.height = 500;
  const ctx = canvas.getContext('2d');

  // 背景を白で塗りつぶす（Canvasが透明になるのを防ぐ）
  ctx.fillStyle = '#FFFFFF';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // 画像を直接読み込む
  const img = new Image();
  img.src = imagePath; 
  
  await new Promise((resolve, reject) => {
    img.onload = resolve;
    img.onerror = (e) => {
      console.error("画像の読み込みに失敗しました:", imagePath, e);
      reject(e);
    };
  });

  // スピまる画像を描画（中央に配置）
  ctx.drawImage(img, 50, 50, 400, 400);

  // 日付テキストを描画
  ctx.font = 'bold 30px sans-serif';
  ctx.fillStyle = '#555';
  ctx.textAlign = 'center';
  ctx.fillText(`${achievedDate} Achieved!`, 250, 480);

  // ダウンロードの実行
  try {
    const link = document.createElement('a');
    link.download = `Spimaru_${stickerId}.png`;
    link.href = canvas.toDataURL('image/png');
    link.click();

    // 💡 【エラー解決のコア】定数エラーを起こしていた const newStickers を撤廃し、直接ステートに代入します
    this.stickers[stickerId] = {
      date: achievedDate,
      downloaded: true,
      specialCostume: matchedHoliday ? matchedHoliday.costumeId : null
    };

    // リアクティブに状態を更新
    this.stickers = { ...this.stickers };

    // 4週目（month1）のダウンロード完了時に、自動で1週目のカードにループさせる
    if (stickerId === 'month1') {
      this.stamps = [];          // スタンプ履歴を真っ新に空っぽにする
      this.dailyCount = 0;       // 今日の運動カウントもリセット
      this.streakCount = 0;      // 継続日数も最初からに戻す
      console.log("🏁 4週目（month1）クリア！スタンプカードを1週目に自動リセットしました！");
    }

    // localStorageに確実に即時保存
    this.saveToLocalStorage();

    console.log(`${stickerId} marked as downloaded and saved to LocalStorage.`);

  } catch (e) {
    console.error("ダウンロード処理に失敗しました:", e);
  }
},

saveToLocalStorage() {
  localStorage.setItem('stampHistory', JSON.stringify(this.stamps));
  localStorage.setItem('dailyCount', this.dailyCount.toString());
  localStorage.setItem('lastSpinDate', this.lastSpinDate);
  localStorage.setItem('streakCount', this.streakCount.toString());
  localStorage.setItem('fitspin_stickers', JSON.stringify(this.stickers));
}
  }
})