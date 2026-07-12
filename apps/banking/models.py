import uuid

from django.conf import settings
from django.db import models


class BankAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bank_accounts",
    )
    account_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    routing_number = models.CharField(max_length=20, null=True, blank=True)
    provider = models.CharField(max_length=50, null=True, blank=True)
    provider_account_id = models.CharField(max_length=255, null=True, blank=True)
    balance_cents = models.BigIntegerField(default=0)
    status = models.CharField(max_length=20, default="ACTIVE")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "bank_accounts"

    def __str__(self):
        return f"{self.user.email} - {self.account_number}"


class BankTransaction(models.Model):
    TYPE_CHOICES = [
        ("DEPOSIT", "Deposit"),
        ("WITHDRAWAL", "Withdrawal"),
        ("TRANSFER_OUT", "Transfer Out"),
        ("TRANSFER_IN", "Transfer In"),
        ("P2P_SENT", "P2P Sent"),
        ("P2P_RECEIVED", "P2P Received"),
        ("CARD_PURCHASE", "Card Purchase"),
        ("BILL_PAYMENT", "Bill Payment"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount_cents = models.BigIntegerField()
    balance_after_cents = models.BigIntegerField()
    description = models.TextField(null=True, blank=True)
    reference = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, default="COMPLETED")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "bank_transactions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.type} {self.amount_cents}"
