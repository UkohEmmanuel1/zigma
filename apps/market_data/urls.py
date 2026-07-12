from django.urls import path

from market_data.views import (
    CandlesView,
    MarketQuoteByTypeView,
    QuoteView,
    SymbolSearchView,
)

app_name = "market_data"

urlpatterns = [
    path("quote/<str:symbol>/", QuoteView.as_view(), name="market-quote"),
    path("quote/<str:market_type>/<str:symbol>/", MarketQuoteByTypeView.as_view(), name="market-quote-by-type"),
    path("candles/<str:symbol>/", CandlesView.as_view(), name="market-candles"),
    path("candles/<str:market_type>/<str:symbol>/", CandlesView.as_view(), name="market-candles-by-type"),
    path("search/", SymbolSearchView.as_view(), name="market-search"),
]
