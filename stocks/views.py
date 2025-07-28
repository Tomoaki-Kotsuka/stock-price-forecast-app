import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import StockForm
from .models import Stock, StockPrediction, StockPrice
from .utils import get_chart_data, simple_prediction, update_stock_prices


def index(request):
    """
    ホームページ - 登録済み銘柄の一覧表示
    """
    stocks = Stock.objects.all().order_by("-created_at")  # 新しい銘柄を一番上に表示
    form = StockForm()

    # 新しい銘柄の追加処理
    if request.method == "POST":
        form = StockForm(request.POST)
        if form.is_valid():
            try:
                stock = form.save()
                # フォームからデモデータ使用フラグを取得
                use_demo = form.cleaned_data.get("use_demo_data", False)

                # 株価データを取得・更新
                update_count, is_demo = update_stock_prices(stock, use_demo=use_demo)

                if update_count:
                    data_type = "デモデータ" if is_demo else "実際のデータ"
                    if is_demo:
                        if use_demo:
                            messages.info(
                                request,
                                f"📊 {stock.name} ({stock.symbol}) を追加し、{update_count}件の{data_type}を取得しました（デモデータを選択）。",
                            )
                        else:
                            messages.warning(
                                request,
                                f"⚠️ {stock.name} ({stock.symbol}) を追加し、{update_count}件の{data_type}を取得しました（Yahoo Finance APIが利用できないため）。",
                            )
                    else:
                        messages.success(
                            request,
                            f"✅ {stock.name} ({stock.symbol}) を追加し、{update_count}件の{data_type}を取得しました。",
                        )
                else:
                    messages.error(
                        request,
                        f"{stock.name} ({stock.symbol}) を追加しましたが、データの取得に失敗しました。",
                    )

                return redirect("stocks:index")
            except Exception as e:
                messages.error(request, f"銘柄の追加中にエラーが発生しました: {str(e)}")
                form.add_error(None, str(e))
        else:
            # フォームエラーをメッセージとして表示
            for field, errors in form.errors.items():
                for error in errors:
                    if field == "__all__":
                        messages.error(request, error)
                    else:
                        field_label = form.fields[field].label or field
                        messages.error(request, f"{field_label}: {error}")

    # 各銘柄の最新価格を取得
    stock_data = []
    for stock in stocks:
        latest_price = StockPrice.objects.filter(stock=stock).order_by("-date").first()
        latest_prediction = (
            StockPrediction.objects.filter(stock=stock).order_by("-created_at").first()
        )

        stock_data.append(
            {
                "stock": stock,
                "latest_price": latest_price,
                "latest_prediction": latest_prediction,
            }
        )

    return render(
        request, "stocks/index.html", {"stock_data": stock_data, "form": form}
    )


def stock_detail(request, symbol):
    """
    個別銘柄の詳細表示
    """
    stock = get_object_or_404(Stock, symbol=symbol)

    # 最新の株価データ（30日分）
    prices = StockPrice.objects.filter(stock=stock).order_by("-date")[:30]

    # チャート用データを取得
    chart_data = get_chart_data(stock, days=30)

    # 最新の予想データ（作成日時順）
    predictions = StockPrediction.objects.filter(stock=stock).order_by("-created_at")[
        :5
    ]

    context = {
        "stock": stock,
        "prices": prices,
        "chart_data": json.dumps(chart_data),
        "predictions": predictions,
    }

    return render(request, "stocks/stock_detail.html", context)


def prediction(request, symbol):
    """
    株価予想の表示・実行
    """
    stock = get_object_or_404(Stock, symbol=symbol)

    prediction_result = None
    if request.method == "POST":
        # 予想を実行
        prediction_result = simple_prediction(stock)
        if prediction_result:
            messages.success(request, "株価予想を実行しました。")
        else:
            messages.error(
                request,
                "株価予想の実行に失敗しました。十分なデータがない可能性があります。",
            )

    # 過去の予想データ（作成日時の新しい順）
    past_predictions = StockPrediction.objects.filter(stock=stock).order_by(
        "-created_at"
    )[:10]

    # 最新の株価データ
    recent_prices = StockPrice.objects.filter(stock=stock).order_by("-date")[:10]

    context = {
        "stock": stock,
        "prediction_result": prediction_result,
        "past_predictions": past_predictions,
        "recent_prices": recent_prices,
    }

    return render(request, "stocks/prediction.html", context)


@require_http_methods(["GET"])
def chart_data_api(request, symbol):
    """
    チャート用データのAPI
    """
    stock = get_object_or_404(Stock, symbol=symbol)
    days = int(request.GET.get("days", 30))

    chart_data = get_chart_data(stock, days=days)

    return JsonResponse(chart_data)


@require_http_methods(["POST"])
def update_stock_data(request, symbol):
    """
    株価データの更新
    """
    stock = get_object_or_404(Stock, symbol=symbol)

    try:
        update_count, is_demo = update_stock_prices(stock)

        if update_count:
            data_type = "デモデータ" if is_demo else "実際のデータ"
            if is_demo:
                messages.warning(
                    request,
                    f"⚠️ {update_count}件の新しい{data_type}を取得しました（Yahoo Finance APIが利用できないため）。",
                )
            else:
                messages.success(
                    request, f"✅ {update_count}件の新しい{data_type}を取得しました。"
                )
        else:
            messages.info(request, "新しいデータはありませんでした。")
    except Exception as e:
        messages.error(request, f"データ更新中にエラーが発生しました: {str(e)}")

    return redirect("stocks:stock_detail", symbol=symbol)


@require_http_methods(["POST"])
def delete_stock(request, symbol):
    """
    銘柄の削除
    """
    stock = get_object_or_404(Stock, symbol=symbol)
    stock_name = stock.name

    try:
        # 関連データも含めて削除（CASCADE設定によりStockPrice、StockPredictionも自動削除）
        stock.delete()
        messages.success(request, f"🗑️ {stock_name} ({symbol}) を削除しました。")
    except Exception as e:
        messages.error(request, f"銘柄削除中にエラーが発生しました: {str(e)}")

    return redirect("stocks:index")
