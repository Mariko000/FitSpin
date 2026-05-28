import { ref } from 'vue'
// ここは純粋に「現在の日時や天気の生データ」を取得してくるだけの「情報源（センサー）」に徹する

export const useWeather = () => {

const weatherType = ref('sunny')

// 現在位置取得関数
const getCurrentLocation = () => {
    return new Promise((resolve, reject) => {
  
      console.log('位置情報取得開始')
  
      navigator.geolocation.getCurrentPosition(
  
        // 成功時
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
  
        // オプション
        {
          enableHighAccuracy: true,
          timeout: 5000,
          maximumAge: 0
        }
      )
    })
  }
  
  const getLocationInfo = async () => {
    try {
      const { lat, lon } = await getCurrentLocation()
      const location = await getLocationName(lat, lon)
  
      return { lat, lon, location }
    } catch (e) {
      console.error('位置情報取得失敗:', e)
  
      return {
        lat: null,
        lon: null,
        location: {
          country: null,
          prefecture: null,
          city: null
        }
      }
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
        data.address?.state ||
        data.address?.region ||
        data.address?.county ||
        data.address?.state_district ||
        data.address?.province ||
        null,

      city:
        data.address?.city ||
        data.address?.town ||
        data.address?.village ||
        data.address?.municipality ||
        data.address?.suburb ||
        data.address?.hamlet ||
        null
    }
  
    } catch (error) {
      console.error('地名取得失敗', error)
  
    // getLocationName() の戻り値を完全固定
    //「null だったらエラーにしないでね」
     return {
        country: null,
        prefecture: null,
        city: null
      }
    }
  }

  // 天気
const fetchWeather = async () => {
    const today = new Date().toISOString().split('T')[0]
  
    console.log('天気取得開始')
  
    try {
      const { lat, lon, location } = await getLocationInfo()

      if (!lat || !lon) {
        weatherType.value = 'sunny'
        return
      }
  
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


  return {
    weatherType,
    fetchWeather,
    fetchPastWeather,
    getCurrentLocation,
    getLocationName,
    getLocationInfo
  }
}
