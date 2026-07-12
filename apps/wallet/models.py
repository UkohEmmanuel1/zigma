import uuid

from django.conf import settings
from django.db import models


class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallet",
    )
    balance_cents = models.BigIntegerField(default=0)
    currency = models.CharField(max_length=3, default="USD")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "wallets"

    def __str__(self):
        return f"{self.user.email} wallet ({self.currency})"


class Transaction(models.Model):
    TYPE_CHOICES = [
        ("DEPOSIT", "Deposit"),
        ("WITHDRAWAL", "Withdrawal"),
        ("TRADE_BUY", "Trade Buy"),
        ("TRADE_SELL", "Trade Sell"),
        ("CRYPTO_BUY", "Crypto Buy"),
        ("CRYPTO_SELL", "Crypto Sell"),
        ("SWAP", "Swap"),
        ("CARD_PURCHASE", "Card Purchase"),
        ("P2P_TRANSFER", "P2P Transfer"),
        ("BILL_PAYMENT", "Bill Payment"),
        ("STAKING_REWARD", "Staking Reward"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount_cents = models.BigIntegerField()
    balance_after_cents = models.BigIntegerField()
    status = models.CharField(max_length=20, default="COMPLETED")
    reference = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transactions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.type} {self.amount_cents} ({self.status})"


class P2PTransfer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_transfers",
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_transfers",
    )
    amount_cents = models.BigIntegerField()
    note = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, default="COMPLETED")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "p2p_transfers"
        ordering = ["-created_at"]
