// src/data/holidayMaster.js
// asset: sunglassesSpimaru,などで登録するだけ
import sunglassesSpimaru from '@/assets/logo/05_wearing_sunglasses.png'

export const holidayMaster = {

// 土日ダウンロード用の専用データ
  'weekend': {
    name: '週末限定ボーナス (Weekend Bonus)',
    costumeId: 'sunglasses',
    title: 'レアスピまる',
    asset: sunglassesSpimaru, // 冒頭でインポートしているアセット
    message: '週末のご褒美！レアスピまる出現中！'
  },
    // --- 春（3月〜5月） ---
    '03-08': {
      name: '国際女性デー (International Women\'s Day)',
      costumeId: 'mimosa',
      title: '花を持つスピまる',
      message: '世界が花で溢れる日！感謝を込めて。'
    },
    '04-22': {
      name: 'アースデイ (Earth Day)',
      costumeId: 'earth',
      title: '地球にやさしいスピまる',
      message: 'かけがえのない地球の環境をみんなで考える日。'
    },
    // --- 夏（6月〜8月） ---
    '06-01': {
      name: '国際子どもの日 (International Children\'s Day)',
      costumeId: 'toy_crown',
      title: 'わんぱくスピまる',
      message: '世界中の子どもたちの幸せを願う日。'
    },
    '06-08': {
      name: '世界海洋デー (World Oceans Day)',
      costumeId: 'diver',
      title: '潜水士スピまる',
      message: '深い青、豊かな海を守る約束の日。'
    },
    '07-20': {
      name: '国際月面着陸の日 (International Moon Day)',
      costumeId: 'astronaut',
      title: '宇宙飛行士スピまる',
      message: '人類が初めて月に一歩を標した歴史的な日！'
    },
  
    // --- 秋（9月〜11月） ---
    '10-05': {
      name: '世界教師デー (World Teachers\' Day)',
      costumeId: 'professor',
      title: 'スピまる教授',
      message: '世界のすべての「先生」に感謝を伝える日。🎓'
    },
    '10-31': {
      name: 'ハロウィン (Halloween)', // 世界的なお祭りイベント
      costumeId: 'wizard',
      title: '魔法使いスピまる',
      message: 'Trick or Treat! お菓子をくれないとイタズラしちゃうぞ！'
    },
    '11-21': {
      name: '世界テレビ・世界ハロー・デー (World Hello Day)',
      costumeId: 'global_hello',
      title: 'フレンドリースピまる',
      message: '世界の平和を願って、今日はいろんな言葉で「ハロー！」'
    },
  
    // --- 冬（12月〜2月） ---
    '12-05': {
      name: '国際ボランティア・デー (International Volunteer Day)',
      costumeId: 'helper',
      title: 'たすけあいスピまる',
      message: '誰かのために、そっと手を差し伸べ合う特別な日'
    },
    '12-25': {
      name: 'クリスマス (Christmas)',
      costumeId: 'santa',
      title: 'サンタスピまる',
      message: 'Merry Christmas! あなたに素敵なプレゼントが届きますように'
    }
  }