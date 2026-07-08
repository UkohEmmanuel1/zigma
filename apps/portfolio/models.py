import uuid

from django.conf import settings
from django.db import models


class Portfolio(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="portfolio",
    )
    cash_balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "portfolio"
        verbose_name = "Portfolio"
        verbose_name_plural = "Portfolios"

    def __str__(self):
        return f"{self.user.email}'s portfolio"


class PortfolioHolding(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name="holdings",
    )
    symbol = models.CharField(max_length=20)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)
    avg_entry_price = models.DecimalField(max_digits=20, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "portfolio_holdings"
        verbose_name = "Portfolio Holding"
        verbose_name_plural = "Portfolio Holdings"
        unique_together = (("portfolio", "symbol"),)

    def __str__(self):
        return f"{self.symbol} x {self.quantity}"


class PortfolioSnapshot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name="snapshots",
    )
    total_value = models.DecimalField(max_digits=20, decimal_places=2)
    cash_balance = models.DecimalField(max_digits=20, decimal_places=2)
    snapshot_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "portfolio_snapshots"
        verbose_name = "Portfolio Snapshot"
        verbose_name_plural = "Portfolio Snapshots"
        unique_together = (("portfolio", "snapshot_date"),)
        ordering = ["-snapshot_date"]

    def __str__(self):
        return f"{self.portfolio.user.email} @ {self.snapshot_date}"
