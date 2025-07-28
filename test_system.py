#!/usr/bin/env python
"""
株価予想システム 統合テストスクリプト
Usage: docker compose exec web python test_system.py
"""

import os
import sys
from datetime import datetime

import django

# Django設定の初期化
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stock_forecast_project.settings")
django.setup()

from stocks.models import Stock
from stocks.utils import get_chart_data, simple_prediction


class SystemTester:
    def __init__(self):
        self.test_results = []

    def log_result(self, test_name, status, message=""):
        """テスト結果をログ"""
        symbol = "✅" if status else "❌"
        self.test_results.append(
            {"name": test_name, "status": status, "message": message}
        )
        print(f"{symbol} {test_name}: {message}")

    def test_stock_display_order(self):
        """銘柄表示順序のテスト"""
        print("\n🧪 Testing Stock Display Order")
        print("-" * 50)

        try:
            stocks = Stock.objects.all().order_by("-created_at")[:5]
            if stocks:
                print("📋 Current top 5 stocks (newest first):")
                for i, stock in enumerate(stocks, 1):
                    print(f"   {i}. {stock.symbol} - {stock.name}")

                # 順序チェック
                is_correct_order = True
                for i in range(len(stocks) - 1):
                    if stocks[i].created_at < stocks[i + 1].created_at:
                        is_correct_order = False
                        break

                self.log_result(
                    "Stock Display Order",
                    is_correct_order,
                    f"Order is {'correct' if is_correct_order else 'incorrect'}",
                )
            else:
                self.log_result("Stock Display Order", False, "No stocks found")

        except Exception as e:
            self.log_result("Stock Display Order", False, f"Error: {e}")

    def test_confidence_system(self):
        """信頼度計算システムのテスト"""
        print("\n🎯 Testing Confidence Calculation System")
        print("-" * 50)

        try:
            test_symbols = ["AAPL", "TSLA", "7203", "META"]
            confidences = []

            for symbol in test_symbols[:4]:  # 最大4銘柄でテスト
                try:
                    stock = Stock.objects.get(symbol=symbol)
                    result = simple_prediction(stock)

                    if result:
                        confidence = result["confidence"]
                        confidences.append(confidence)
                        print(f"   📊 {symbol}: {confidence:.2f}% confidence")
                    else:
                        print(f"   ❌ {symbol}: Prediction failed")

                except Stock.DoesNotExist:
                    print(f"   ⏭️  {symbol}: Not found")
                    continue

            if confidences:
                confidence_range = max(confidences) - min(confidences)
                avg_confidence = sum(confidences) / len(confidences)

                # 多様性チェック（範囲が5%以上あれば良好）
                is_diverse = confidence_range >= 5.0

                print("\n📈 Confidence Statistics:")
                print(
                    f"   Range: {confidence_range:.2f}% (High: {max(confidences):.2f}%, Low: {min(confidences):.2f}%)"
                )
                print(f"   Average: {avg_confidence:.2f}%")

                self.log_result(
                    "Confidence Diversity",
                    is_diverse,
                    f"Range: {confidence_range:.2f}% ({'Good' if is_diverse else 'Limited'} diversity)",
                )

                # 50%以上チェック
                above_50 = all(c >= 50.0 for c in confidences)
                self.log_result(
                    "Confidence Threshold",
                    above_50,
                    f"All predictions {'≥' if above_50 else '<'} 50%",
                )
            else:
                self.log_result("Confidence System", False, "No predictions succeeded")

        except Exception as e:
            self.log_result("Confidence System", False, f"Error: {e}")

    def test_chart_data_format(self):
        """チャートデータフォーマットのテスト"""
        print("\n📊 Testing Chart Data Format")
        print("-" * 50)

        try:
            stock = Stock.objects.first()
            if not stock:
                self.log_result("Chart Data Format", False, "No stocks available")
                return

            chart_data = get_chart_data(stock, days=7)

            if chart_data and chart_data["dates"]:
                dates = chart_data["dates"]
                print(f"📅 Sample dates: {' | '.join(dates[:5])}")

                # MM/DD フォーマットチェック
                is_correct_format = all(
                    len(date.split("/")) == 2 and len(date) <= 5 for date in dates[:5]
                )

                # データ完整性チェック
                has_complete_data = (
                    len(chart_data["dates"])
                    == len(chart_data["prices"])
                    == len(chart_data["volumes"])
                )

                self.log_result(
                    "Date Format",
                    is_correct_format,
                    f"Format: {'MM/DD (correct)' if is_correct_format else 'Incorrect format'}",
                )

                self.log_result(
                    "Data Completeness",
                    has_complete_data,
                    f"Data points: dates={len(chart_data['dates'])}, prices={len(chart_data['prices'])}, volumes={len(chart_data['volumes'])}",
                )

            else:
                self.log_result("Chart Data Format", False, "No chart data available")

        except Exception as e:
            self.log_result("Chart Data Format", False, f"Error: {e}")

    def test_system_integration(self):
        """システム統合テスト"""
        print("\n🔄 Testing System Integration")
        print("-" * 50)

        try:
            total_stocks = Stock.objects.count()
            stocks_with_data = (
                Stock.objects.filter(prices__isnull=False).distinct().count()
            )

            print("📊 System Status:")
            print(f"   Total stocks: {total_stocks}")
            print(f"   Stocks with price data: {stocks_with_data}")

            # 基本的な機能チェック
            has_stocks = total_stocks > 0
            has_price_data = stocks_with_data > 0

            self.log_result(
                "Basic Data Availability",
                has_stocks and has_price_data,
                f"Stocks: {total_stocks}, With data: {stocks_with_data}",
            )

            if has_stocks:
                # ランダムな銘柄で統合テスト
                test_stock = Stock.objects.first()

                # 予想実行テスト
                prediction_result = simple_prediction(test_stock)
                prediction_works = prediction_result is not None

                # チャートデータ取得テスト
                chart_result = get_chart_data(test_stock, days=5)
                chart_works = (
                    chart_result is not None and len(chart_result.get("dates", [])) > 0
                )

                self.log_result(
                    "Prediction System",
                    prediction_works,
                    f"Test with {test_stock.symbol}: {'Success' if prediction_works else 'Failed'}",
                )

                self.log_result(
                    "Chart System",
                    chart_works,
                    f"Test with {test_stock.symbol}: {'Success' if chart_works else 'Failed'}",
                )

        except Exception as e:
            self.log_result("System Integration", False, f"Error: {e}")

    def run_all_tests(self):
        """全テストを実行"""
        print("🚀 Stock Price Forecast System - Comprehensive Test")
        print("=" * 70)
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 各テストを実行
        self.test_stock_display_order()
        self.test_confidence_system()
        self.test_chart_data_format()
        self.test_system_integration()

        # 結果サマリー
        print("\n" + "=" * 70)
        print("📋 TEST SUMMARY")
        print("=" * 70)

        passed = sum(1 for result in self.test_results if result["status"])
        total = len(self.test_results)

        for result in self.test_results:
            symbol = "✅" if result["status"] else "❌"
            print(f"{symbol} {result['name']}")
            if result["message"]:
                print(f"    → {result['message']}")

        print(f"\n🎯 Results: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All tests passed! System is working correctly.")
        else:
            print(f"⚠️  {total - passed} test(s) failed. Please check the issues above.")

        print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        return passed == total


if __name__ == "__main__":
    tester = SystemTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
