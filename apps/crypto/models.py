import uuid

from django.conf import settings
from django.db import models


class CryptoWallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="crypto_wallets",
    )
    currency = models.CharField(max_length=10)
    balance = models.DecimalField(max_digits=38, decimal_places=18, default=0)
    address = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "crypto_wallets"
        unique_together = (("user", "currency"),)

    def __str__(self):
        return f"{self.user.email} {self.currency}"


class CryptoOrder(models.Model):
    SIDE_CHOICES = [("BUY", "Buy"), ("SELL", "Sell")]
    TYPE_CHOICES = [("MARKET", "Market"), ("LIMIT", "Limit")]
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("FILLED", "Filled"),
        ("PARTIAL", "Partially Filled"),
        ("CANCELLED", "Cancelled"),
        ("REJECTED", "Rejected"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="crypto_orders",
    )
    symbol = models.CharField(max_length=20)
    side = models.CharField(max_length=4, choices=SIDE_CHOICES)
    order_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=38, decimal_places=18)
    price = models.DecimalField(max_digits=38, decimal_places=18, null=True, blank=True)
    filled_quantity = models.DecimalField(max_digits=38, decimal_places=18, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    is_paper = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    executed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "crypto_orders"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.side} {self.symbol} ({self.status})"


class CryptoHolding(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="crypto_holdings",
    )
    symbol = models.CharField(max_length=20)
    quantity = models.DecimalField(max_digits=38, decimal_places=18, default=0)
    avg_entry_price = models.DecimalField(max_digits=38, decimal_places=18, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "crypto_holdings"
        unique_together = (("user", "symbol"),)

    def __str__(self):
        return f"{self.symbol} x {self.quantity}"


class CryptoSwa(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
        ("CANCELLED", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="crypto_swaps",
    )
    from_currency = models.CharField(max_length=10)
    to_currency = models.CharField(max_length=10)
    from_amount = models.DecimalField(max_digits=38, decimal_places=18)
    to_amount = models.DecimalField(max_digits=38, decimal_places=18, null=True, blank=True)
    rate = models.DecimalField(max_digits=38, decimal_places=18, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    is_paper = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    executed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "crypto_swaps"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.from_currency} -> {self.to_currency} ({self.status})"
