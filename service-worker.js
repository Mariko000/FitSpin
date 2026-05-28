self.addEventListener('install', (event) => {
  self.skipWaiting(); // すぐに新しいSWを有効にする
});

self.addEventListener('activate', (event) => {
  event.waitUntil(clients.claim()); // すぐにページを支配下に置く
});


// 1. サーバーからのプッシュ通知用
self.addEventListener('push', event => {
  const data = event.data ? event.data.text() : '運動しよう！';
  event.waitUntil(
    self.registration.showNotification('FitSpin', {
      body: data,
      icon: '/asset/ghost.png' // 格納先に合わせました
    })
  );
});

// 2. アプリ（Vue）からのタイマー通知（SCHEDULE_GHOST）を受け取った時の処理
// タイマーIDを外側で保持（古いタイマーをキャンセルできるようにする）
let ghostTimerId = null;

self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SCHEDULE_GHOST') {
    const delay = 5 * 1000; // テスト用5秒

    // もし動いているタイマーがあればキャンセルして上書き
    if (ghostTimerId) {
      clearTimeout(ghostTimerId);
    }

    console.log('お化けのスケジュールを更新しました...');

    event.waitUntil(
      new Promise((resolve) => {
        ghostTimerId = setTimeout(async () => {
          try {
            // 同じタグの古い通知を消す
            const notifications = await self.registration.getNotifications({ tag: 'ghost-notif' });
            notifications.forEach(n => n.close());

            // 新しい通知を出す
            await self.registration.showNotification('お化けが呼びに来ました', {
              body: 'そろそろ回さないと、お化けが画面を占領しちゃうよ？',
              icon: '/asset/ghost.png',
              tag: 'ghost-notif',
              renotify: true, // 同じタグでも音やポップアップを強制する
              vibrate: [200, 100, 200],
              requireInteraction: true // ユーザーが閉じるまで消さない（お化け感アップ）
            });
          } catch (err) {
            console.error('Notification error:', err);
          } finally {
            ghostTimerId = null;
            resolve();
          }
        }, delay);
      })
    );
  }
});

// 3. 通知をクリックした時にアプリ（タブ）を開く
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      // すでにアプリが開いていればそこにフォーカス、なければ新規で開く
      for (const client of clientList) {
        if (client.url === '/' && 'focus' in client) return client.focus();
      }
      if (clients.openWindow) return clients.openWindow('/');
    })
  );
});