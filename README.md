# 株価予想アプリ

Djangoを使用した株価予想アプリケーションです。Dockerを使って簡単にセットアップできます。

## 機能
- 株価データの取得・表示
- インタラクティブなチャート表示
- 移動平均による株価予想
- レスポンシブデザイン

## セットアップ（Docker）

1. プロジェクトのクローン
```bash
git clone <repository-url>
cd stock-price-forecast-app
```

2. Dockerでアプリケーションを起動
```bash
docker compose up --build
```

3. ブラウザでアクセス
```
http://localhost:8000
```

## 主な機能

### 銘柄管理
- 日本株の証券コード（例：7203、9984）で銘柄を追加
- Yahoo Finance APIから自動的に株価データを取得

### 株価チャート
- Chart.jsによるインタラクティブなチャート表示
- 過去30日間の株価推移を可視化

### 株価予想
- 5日移動平均と20日移動平均によるトレンド分析
- 簡易的な価格予想と信頼度の表示
- 予想履歴の管理

## 使用技術
- **バックエンド**: Django 5.0
- **データベース**: PostgreSQL 15
- **フロントエンド**: Bootstrap 5, Chart.js
- **コンテナ**: Docker, Docker Compose
- **株価API**: yfinance
- **データ処理**: pandas, numpy
- **機械学習**: scikit-learn, RandomForest, LinearRegression

## テスト実行

システムの動作確認のため、統合テストを実行できます：

### 方法1: シェルスクリプト実行（推奨）
```bash
./run_tests.sh
```

### 方法2: 直接実行
```bash
docker compose exec web python test_system.py
```

### テスト内容
- 銘柄表示順序の確認
- 信頼度計算システムの動作確認（50%以上保証）
- チャートデータフォーマットの確認（MM/DD形式）
- システム統合テスト

## API エンドポイント
- `/` - ホームページ（銘柄一覧）
- `/stock/<symbol>/` - 個別銘柄詳細
- `/prediction/<symbol>/` - 株価予想
- `/api/chart-data/<symbol>/` - チャートデータAPI

## 注意事項
この予想システムは教育・デモンストレーション目的で作成されています。実際の投資判断には使用しないでください。 