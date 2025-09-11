<template>
  <div id="app" class="font-sans antialiased text-gray-900 bg-gray-100 min-h-screen">
    
    <!-- 共通ヘッダーコンポーネントの挿入 -->
    <Header />

    <!-- メインコンテンツ (App.vueがデータ表示も担当) -->
    <main class="container mx-auto p-4 md:p-8">
      <h1 class="text-3xl font-bold mb-4 text-center text-gray-800">Vue.js メインコンテンツ</h1>
      <p class="text-lg text-center text-gray-600 mb-8">
        ここはVue.jsアプリケーションのメインページです。<br>
        上のヘッダーからDjangoのサイトに戻ることができます。
      </p>
       <!-- App.vue がアプリケーションの中心的なロジック（データの取得など）を担う -->
       <!-- ユーザーの認証自体はDjangoからVue.jsのページに引き継がれているはず -->
    </main>
  </div>
</template>

<script>
import { ref } from 'vue';
import axios from 'axios';
import Header from './components/shared/Header.vue';

axios.defaults.xsrfHeaderName = "X-CSRFToken";
axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.withCredentials = true;

export default {
  name: 'App',
  components: {
    Header
  },
  setup() {
    const data = ref(null);
    const error = ref(null);
    const loading = ref(false);

    const fetchProtectedData = async () => {
      data.value = null;
      error.value = null;
      loading.value = true;
      
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/users/current-user/');
        data.value = response.data;
      } catch (err) {
        if (err.response) {
          if (err.response.status === 403) {
            error.value = '認証に失敗しました。ログインしているか確認してください。';
          } else if (err.response.status === 404) {
            error.value = '指定されたAPIエンドポイントが見つかりません。';
          } else {
            error.value = `APIリクエスト中にエラーが発生しました: ${err.message}`;
          }
        } else {
          error.value = `ネットワークエラーが発生しました: ${err.message}`;
        }
      } finally {
        loading.value = false;
      }
    };

    return {
      data,
      error,
      loading,
      fetchProtectedData
    };
  }
};
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

#app {
  font-family: 'Inter', sans-serif;
}
</style>
