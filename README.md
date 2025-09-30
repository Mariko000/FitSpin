# FitSpin

FitSpin はフィットネス管理アプリです。

## 特徴
- ワークアウトの記録
- タイマー機能
- ステータス管理

## インストール

1. リポジトリをクローン
   ```bash
   git clone https://github.com/Mariko000/FitSpin.git
   cd FitSpin
仮想環境作成

bash
Copy code
python -m venv env
仮想環境をアクティベート

bash
Copy code
source env/bin/activate
必要パッケージをインストール

bash
Copy code
pip install -r requirements.txt
Vue.js の依存関係をインストール

bash
Copy code
npm install
使い方
Django 開発サーバー
サーバー起動

bash
Copy code
python manage.py runserver
ブラウザでアクセス

cpp
Copy code
http://127.0.0.1:8000/
Vue.js 開発サーバー
起動

bash
Copy code
npm run dev
ブラウザでアクセス

arduino
Copy code
http://localhost:5173/
ポイント: Django と Vue.js は 両方同時に起動する必要があります。

本番環境
ビルド

bash
Copy code
npm run build
仮想環境の操作
無効化

bash
Copy code
deactivate
データベースマイグレーション
bash
Copy code
python manage.py makemigrations
python manage.py migrate
メモ
Django はバックエンド API や管理画面の提供

Vue.js はフロントエンド SPA の提供

開発時は両方のサーバーを走らせて確認

本番環境では Vue.js をビルドして Django に統合
