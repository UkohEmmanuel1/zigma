from rest_framework import serializers

from wallet.models import P2PTransfer, Transaction, Wallet


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ["id", "balance_cents", "currency", "created_at", "updated_at"]
        read_only_fields = ["id", "balance_cents", "created_at", "updated_at"]


class DepositSerializer(serializers.Serializer):
    amount_cents = serializers.IntegerField(min_value=1)

    def validate_amount_cents(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id", "type", "amount_cents", "balance_after_cents",
            "status", "reference", "description", "created_at",
        ]
        read_only_fields = fields


class P2PTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = P2PTransfer
        fields = "__all__"
        read_only_fields = ["id", "status", "created_at"]
