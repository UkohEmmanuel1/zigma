from rest_framework import serializers

from banking.models import BankAccount, BankTransaction


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = [
            "id", "account_number", "routing_number", "provider",
            "balance_cents", "status", "created_at",
        ]
        read_only_fields = ["id", "account_number", "balance_cents", "status", "created_at"]


class BankAccountCreateSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=["STRIPE", "PAYSTACK"], required=False, default="STRIPE")


class BankTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankTransaction
        fields = [
            "id", "type", "amount_cents", "balance_after_cents",
            "description", "reference", "status", "created_at",
        ]
        read_only_fields = fields


class ExternalTransferSerializer(serializers.Serializer):
    amount_cents = serializers.IntegerField(min_value=1)
    recipient_account_number = serializers.CharField(max_length=50)
    recipient_routing = serializers.CharField(max_length=20)
    note = serializers.CharField(max_length=255, required=False, allow_blank=True)


class P2PSerializer(serializers.Serializer):
    recipient_email = serializers.EmailField()
    amount_cents = serializers.IntegerField(min_value=1)
    note = serializers.CharField(max_length=255, required=False, allow_blank=True)


class BillPaySerializer(serializers.Serializer):
    amount_cents = serializers.IntegerField(min_value=1)
    biller_code = serializers.CharField(max_length=50)
    biller_account = serializers.CharField(max_length=50)
    note = serializers.CharField(max_length=255, required=False, allow_blank=True)
