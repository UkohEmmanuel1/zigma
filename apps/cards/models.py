import uuid

from django.conf import settings
from django.db import models


class BankCard(models.Model):
    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("FROZEN", "Frozen"),
        ("CANCELLED", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cards",
    )
    provider = models.CharField(max_length=50)
    provider_card_id = models.CharField(max_length=255)
    last4 = models.CharField(max_length=4)
    expiry_month = models.IntegerField(null=True, blank=True)
    expiry_year = models.IntegerField(null=True, blank=True)
    brand = models.CharField(max_length=20, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ACTIVE")
    daily_limit_cents = models.BigIntegerField(null=True, blank=True)
    monthly_limit_cents = models.BigIntegerField(null=True, blank=True)
    online_enabled = models.BooleanField(default=True)
    atm_enabled = models.BooleanField(default=False)
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "bank_cards"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.brand} ****{self.last4} ({self.status})"
