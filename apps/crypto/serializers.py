from decimal import Decimal

from rest_framework import serializers

from crypto.models import CryptoHolding, CryptoOrder, CryptoSwa, CryptoWallet
from crypto.services import SUPPORTED_CRYPTO


class CryptoWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = CryptoWallet
        fields = ["id", "currency", "balance", "address", "created_at"]
        read_only_fields = ["id", "balance", "created_at"]


class CryptoOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CryptoOrder
        fields = [
            "id", "symbol", "side", "order_type", "quantity", "price",
            "filled_quantity", "status", "is_paper", "created_at", "executed_at",
        ]
        read_only_fields = ["id", "filled_quantity", "status", "created_at", "executed_at"]


class CryptoOrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CryptoOrder
        fields = ["symbol", "side", "order_type", "quantity", "price", "is_paper"]

    def validate_side(self, value):
        if value.upper() not in ("BUY", "SELL"):
            raise serializers.ValidationError('Side must be "BUY" or "SELL".')
        return value.upper()

    def validate_order_type(self, value):
        if value.upper() not in ("MARKET", "LIMIT"):
            raise serializers.ValidationError('Order type must be "MARKET" or "LIMIT".')
        return value.upper()

    def validate(self, attrs):
        if attrs["order_type"] == "LIMIT" and not attrs.get("price"):
            raise serializers.ValidationError("Price is required for limit orders.")
        return attrs


class CryptoHoldingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CryptoHolding
        fields = ["id", "symbol", "quantity", "avg_entry_price", "created_at", "updated_at"]
        read_only_fields = fields


class CryptoSwaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CryptoSwa
        fields = [
            "id", "from_currency", "to_currency", "from_amount", "to_amount",
            "rate", "status", "is_paper", "created_at", "executed_at",
        ]
        read_only_fields = ["id", "to_amount", "rate", "status", "created_at", "executed_at"]


class CryptoSwaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CryptoSwa
        fields = ["from_currency", "to_currency", "from_amount", "is_paper"]

    def validate_from_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value

    def validate(self, attrs):
        if attrs["from_currency"] == attrs["to_currency"]:
            raise serializers.ValidationError("From and to currencies must be different.")
        return attrs


class CryptoBuySerializer(serializers.Serializer):
    from_currency = serializers.ChoiceField(choices=["USD"], default="USD")
    to_currency = serializers.ChoiceField(choices=sorted(SUPPORTED_CRYPTO))
    amount_cents = serializers.IntegerField(min_value=1)

    def validate_amount_cents(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value


class CryptoSellSerializer(serializers.Serializer):
    from_currency = serializers.ChoiceField(choices=sorted(SUPPORTED_CRYPTO))
    to_currency = serializers.ChoiceField(choices=["USD"], default="USD")
    quantity = serializers.DecimalField(max_digits=38, decimal_places=18, min_value=Decimal("0.00000001"))

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be positive.")
        return value
