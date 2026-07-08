from decimal import Decimal

from rest_framework import serializers

from market_data.models import MarketQuote
from portfolio.models import Portfolio, PortfolioHolding, PortfolioSnapshot


class PortfolioHoldingSerializer(serializers.ModelSerializer):
    current_price = serializers.SerializerMethodField()
    market_value = serializers.SerializerMethodField()
    unrealized_pl = serializers.SerializerMethodField()
    return_pct = serializers.SerializerMethodField()

    class Meta:
        model = PortfolioHolding
        fields = [
            "symbol", "quantity", "avg_entry_price",
            "current_price", "market_value", "unrealized_pl", "return_pct",
        ]

    def get_current_price(self, obj):
        try:
            quote = MarketQuote.objects.get(symbol=obj.symbol)
            return quote.last
        except MarketQuote.DoesNotExist:
            return None

    def get_market_value(self, obj):
        price = self.get_current_price(obj)
        if price is None:
            return None
        return float(price) * float(obj.quantity)

    def get_unrealized_pl(self, obj):
        price = self.get_current_price(obj)
        if price is None:
            return None
        return (float(price) - float(obj.avg_entry_price)) * float(obj.quantity)

    def get_return_pct(self, obj):
        price = self.get_current_price(obj)
        if price is None or float(obj.avg_entry_price) == 0:
            return None
        return ((float(price) - float(obj.avg_entry_price)) / float(obj.avg_entry_price)) * 100


class PortfolioSerializer(serializers.ModelSerializer):
    holdings = PortfolioHoldingSerializer(many=True, read_only=True)
    total_value = serializers.SerializerMethodField()

    class Meta:
        model = Portfolio
        fields = ["cash_balance", "total_value", "holdings"]

    def get_total_value(self, obj):
        total = float(obj.cash_balance)
        for holding in obj.holdings.all():
            price_ser = PortfolioHoldingSerializer(holding)
            mv = price_ser.data.get("market_value")
            if mv is not None:
                total += mv
        return round(total, 2)


class PortfolioPerformanceSerializer(serializers.ModelSerializer):
    daily_return = serializers.SerializerMethodField()

    class Meta:
        model = PortfolioSnapshot
        fields = ["snapshot_date", "total_value", "cash_balance", "daily_return"]

    def get_daily_return(self, obj):
        prev = (
            PortfolioSnapshot.objects
            .filter(portfolio=obj.portfolio, snapshot_date__lt=obj.snapshot_date)
            .order_by("-snapshot_date")
            .first()
        )
        if prev is None or float(prev.total_value) == 0:
            return None
        return round(
            (float(obj.total_value) - float(prev.total_value)) / float(prev.total_value) * 100,
            2,
        )
