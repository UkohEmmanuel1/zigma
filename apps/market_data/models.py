import uuid

from django.db import models


class MarketQuote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    symbol = models.CharField(max_length=20)
    bid = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    ask = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    last = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    volume = models.DecimalField(max_digits=30, decimal_places=8, null=True, blank=True)
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "market_quotes"
        verbose_name = "Market Quote"
        verbose_name_plural = "Market Quotes"

    def __str__(self):
        return f"{self.symbol} @ {self.timestamp}"


class PriceHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    symbol = models.CharField(max_length=20)
    interval = models.CharField(max_length=10)
    open = models.DecimalField(max_digits=20, decimal_places=8)
    high = models.DecimalField(max_digits=20, decimal_places=8)
    low = models.DecimalField(max_digits=20, decimal_places=8)
    close = models.DecimalField(max_digits=20, decimal_places=8)
    volume = models.DecimalField(max_digits=30, decimal_places=8)
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "price_history"
        verbose_name = "Price History"
        verbose_name_plural = "Price Histories"
        unique_together = (("symbol", "interval", "timestamp"),)

    def __str__(self):
        return f"{self.symbol} [{self.interval}] @ {self.timestamp}"


class WatchedSymbol(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    symbol = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "market_watched_symbols"
        verbose_name = "Watched Symbol"
        verbose_name_plural = "Watched Symbols"

    def __str__(self):
        return self.symbol
