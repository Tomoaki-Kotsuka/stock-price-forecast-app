from django.contrib import admin

from .models import Stock, StockPrediction, StockPrice


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("symbol", "name", "exchange", "created_at")
    list_filter = ("exchange", "created_at")
    search_fields = ("symbol", "name")


@admin.register(StockPrice)
class StockPriceAdmin(admin.ModelAdmin):
    list_display = ("stock", "date", "close_price", "volume")
    list_filter = ("stock", "date")
    search_fields = ("stock__symbol", "stock__name")
    date_hierarchy = "date"


@admin.register(StockPrediction)
class StockPredictionAdmin(admin.ModelAdmin):
    list_display = (
        "stock",
        "prediction_date",
        "predicted_price",
        "confidence",
        "method",
    )
    list_filter = ("method", "prediction_date")
    search_fields = ("stock__symbol", "stock__name")
