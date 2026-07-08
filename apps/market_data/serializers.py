from rest_framework import serializers

from market_data.models import MarketQuote, PriceHistory, WatchedSymbol


class MarketQuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketQuote
        fields = ["symbol", "bid", "ask", "last", "volume", "timestamp"]


class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceHistory
        fields = ["symbol", "interval", "open", "high", "low", "close", "volume", "timestamp"]


class WatchedSymbolSerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchedSymbol
        fields = ["id", "symbol", "is_active", "created_at", "updated_at"]
