#!/bin/bash

echo "🚀 Running Stock Price Forecast System Tests..."
echo ""

# Dockerコンテナが動いているかチェック
if ! docker compose ps | grep -q "web.*Up"; then
    echo "❌ Docker containers are not running. Starting them..."
    docker compose up -d
    echo "⏳ Waiting for services to be ready..."
    sleep 10
fi

# テスト実行
echo "▶️  Executing test_system.py..."
docker compose exec web python test_system.py

echo ""
echo "✅ Test execution completed!" 