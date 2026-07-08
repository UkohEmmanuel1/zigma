from django.urls import path

from market_data.views import CandlesView, QuoteView, SymbolSearchView

app_name = "market_data"

urlpatterns = [
    path("quote/<str:symbol>/", QuoteView.as_view(), name="market-quote"),
    path("candles/<str:symbol>/", CandlesView.as_view(), name="market-candles"),
    path("search/", SymbolSearchView.as_view(), name="market-search"),
]
