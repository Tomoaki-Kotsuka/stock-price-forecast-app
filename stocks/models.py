from django.db import models


class Stock(models.Model):
    """株式銘柄のモデル"""

    symbol = models.CharField(
        max_length=10, unique=True, verbose_name="ティッカーシンボル"
    )
    name = models.CharField(max_length=100, verbose_name="銘柄名")
    exchange = models.CharField(max_length=10, verbose_name="市場", default="TSE")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "株式銘柄"
        verbose_name_plural = "株式銘柄"

    def __str__(self):
        return f"{self.symbol} - {self.name}"


class StockPrice(models.Model):
    """株価データのモデル"""

    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name="prices")
    date = models.DateField(verbose_name="日付")
    open_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="始値"
    )
    high_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="高値"
    )
    low_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="安値"
    )
    close_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="終値"
    )
    volume = models.BigIntegerField(verbose_name="出来高")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "株価データ"
        verbose_name_plural = "株価データ"
        unique_together = ["stock", "date"]
        ordering = ["-date"]

    def __str__(self):
        return f"{self.stock.symbol} - {self.date}: ¥{self.close_price}"


class StockPrediction(models.Model):
    """株価予想のモデル"""

    stock = models.ForeignKey(
        Stock, on_delete=models.CASCADE, related_name="predictions"
    )
    prediction_date = models.DateField(verbose_name="予測日")
    predicted_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="予測価格"
    )
    confidence = models.FloatField(verbose_name="信頼度", default=0.0)
    method = models.CharField(
        max_length=50, verbose_name="予測手法", default="移動平均"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "株価予想"
        verbose_name_plural = "株価予想"
        ordering = ["-created_at"]  # 作成日時の新しい順

    def __str__(self):
        return f"{self.stock.symbol} - {self.prediction_date}: ¥{self.predicted_price}"
