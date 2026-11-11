import uuid

from django.conf import settings
from django.db import models


class ConnectedWallet(models.Model):
    """A public address associated with a user; never stores keys or seed phrases."""

    class Chain(models.TextChoices):
        ETHEREUM = "ethereum", "Ethereum"
        BNB = "bnb", "BNB Smart Chain"
        POLYGON = "polygon", "Polygon"
        BITCOIN = "bitcoin", "Bitcoin"
        SOLANA = "solana", "Solana"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="connected_wallets")
    chain = models.CharField(max_length=16, choices=Chain.choices)
    address = models.CharField(max_length=128)
    label = models.CharField(max_length=40, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "connected_wallets"
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["user", "chain", "address"], name="uniq_user_chain_address")]
        indexes = [models.Index(fields=["chain", "address"])]

    def __str__(self):
        return f"{self.chain}:{self.address}"
