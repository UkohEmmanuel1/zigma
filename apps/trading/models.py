import uuid

from django.conf import settings
from django.db import models


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    symbol = models.CharField(max_length=20)
    side = models.CharField(max_length=4)
    order_type = models.CharField(max_length=10)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)
    price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    stop_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    filled_quantity = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "trading_orders"
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"{self.side} {self.symbol} {self.order_type} ({self.status})"


class Holding(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="holdings",
    )
    symbol = models.CharField(max_length=20)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)
    avg_entry_price = models.DecimalField(max_digits=20, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "trading_holdings"
        verbose_name = "Holding"
        verbose_name_plural = "Holdings"
        unique_together = (("user", "symbol"),)

    def __str__(self):
        return f"{self.symbol} x {self.quantity}"
