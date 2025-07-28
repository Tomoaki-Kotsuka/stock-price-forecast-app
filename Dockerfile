FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# システムの依存関係をインストール
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Pythonの依存関係をコピー・インストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# ポート8000を公開
EXPOSE 8000

# Django開発サーバーを起動
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] 