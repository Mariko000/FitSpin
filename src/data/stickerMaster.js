
// 「どのステッカーが、何日達成で解放されるか、画像パスは何か」という「マスターデータ（辞書）」
import crown from '@/assets/logo/01_wearing_crown.png'
import necklace from '@/assets/logo/02_wearing_necklace.png'
import trainer from '@/assets/logo/03_wearing_trainer.png'
import dumbbell from '@/assets/logo/04_holding_dumbbell.png'

export const stickerMaster = {
    week1: {
      id: 'week1',
      asset: crown,
      needed: 7,
      title: '1週間',
      achievedMessage: '🎉 1週間達成！スピまるからプレゼントがあるよ！',
      normalMessage: 'また次の1週間も頑張ろうね！',
    },
    week2: {
      id: 'week2',
      asset: necklace,
      needed: 14,
      title: '2週間',
      achievedMessage: '🎉 2週間達成！スピまるからプレゼントがあるよ！',
      normalMessage: 'また次の1週間も頑張ろうね！',
    },
    week3: {
      id: 'week3',
      asset: trainer,
      needed: 21,
      title: '3週間',
      achievedMessage: '🎉 3週間達成！スピまるからプレゼントがあるよ！',
      normalMessage: 'また次の1週間も頑張ろうね！',
    },
    month1: {
      id: 'month1',
      asset: dumbbell,
      needed: 30,
      title: '1ヶ月',
      achievedMessage: '🎉 1ヶ月達成！スピまるからプレゼントがあるよ！',
      normalMessage: 'また次のチャレンジも頑張ろうね！',
    },
  }