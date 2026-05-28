<!-- src/App.vue -->
<template>
  <div class="app-layout">
  <Header />
  <router-view />   <!-- ここに各ページがレンダリングされる -->
</div>
</template>

<script setup>
import Header from './components/shared/Header.vue'
import './assets/css/main.css'
import { onMounted } from 'vue'

const requestNotificationPermission = async () => {
  if ('Notification' in window) {
    const permission = await Notification.requestPermission();
    if (permission === 'granted') {
      console.log('お化けの呼び出し許可をいただきました...');
    }
  }
};

onMounted(() => {
  console.log('App mounted!')
  
  // 1. マウント時に通知の許可を求める
  requestNotificationPermission();

  // 2. Service Worker 登録
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/service-worker.js')
        .then(registration => {
          console.log('Service Worker registered', registration);
        })
        .catch(error => console.error('Service Worker registration failed', error));
    });
  }
})
</script>

<style>
body {
  padding:0;
  margin:0;
  width: 100%;
  
}
#app {
  display: flex;
  flex-direction: column; /* ←縦に積む */
  padding:0;
  margin:0;
  width: 100%;
}

/* もし body に flex が当たっている場合はリセット */
body {
  display: block; /* もしくは flex-direction:column; */
}

/* アプリ全体のベース */
.app-layout {
  min-height: 100vh;
  background-color: #FFFDE7; /* アプリ全体の背景色をここで統一 */
}

/* ★ これが魔法のレスポンシブコンテナ */
.main-container {
  width: 100%;
  /* 左右に必ず「16px」のクッションを確保（スマホで端っこにペタッとくっつかなくなる） */
  padding: 20px 16px; 
  
  /* PCやタブレットで横に広がりすぎないように制限 */
  max-width: 500px; /* スマホ型アプリとして最適なサイズ感 */
  margin: 0 auto;   /* 画面の中央に寄せる */
  
  box-sizing: border-box;
}

/* タブレットやPCなど、画面幅に余裕があるとき */
@media (min-width: 600px) {
  .main-container {
    padding: 40px 24px; /* ゆったりした空間にする */
  }
}
</style>