from django.urls import path

from . import views

app_name = "stocks"

urlpatterns = [
    path("", views.index, name="index"),
    path("stock/<str:symbol>/", views.stock_detail, name="stock_detail"),
    path("prediction/<str:symbol>/", views.prediction, name="prediction"),
    path("api/chart-data/<str:symbol>/", views.chart_data_api, name="chart_data_api"),
    path(
        "update-stock/<str:symbol>/", views.update_stock_data, name="update_stock_data"
    ),
    path("delete-stock/<str:symbol>/", views.delete_stock, name="delete_stock"),
]
