from rest_framework import serializers

from cards.models import BankCard


class BankCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankCard
        fields = [
            "id", "last4", "expiry_month", "expiry_year", "brand",
            "status", "daily_limit_cents", "monthly_limit_cents",
            "online_enabled", "atm_enabled", "created_at",
        ]
        read_only_fields = ["id", "last4", "expiry_month", "expiry_year", "brand", "status", "created_at"]


class BankCardCreateSerializer(serializers.Serializer):
    brand = serializers.ChoiceField(choices=["VISA", "MASTERCARD"], default="VISA")


class CardLimitSerializer(serializers.Serializer):
    daily_limit_cents = serializers.IntegerField(min_value=0, required=False)
    monthly_limit_cents = serializers.IntegerField(min_value=0, required=False)


class CardToggleSerializer(serializers.Serializer):
    enabled = serializers.BooleanField()
