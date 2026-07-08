from rest_framework import serializers

from trading.models import Holding, Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id", "symbol", "side", "order_type", "quantity",
            "price", "stop_price", "filled_quantity", "status",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "filled_quantity", "status", "created_at", "updated_at"]


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["symbol", "side", "order_type", "quantity", "price", "stop_price"]

    def validate_side(self, value):
        if value not in ("buy", "sell"):
            raise serializers.ValidationError('Side must be "buy" or "sell".')
        return value

    def validate_order_type(self, value):
        if value not in ("market", "limit", "stop"):
            raise serializers.ValidationError('Order type must be "market", "limit", or "stop".')
        return value

    def validate(self, attrs):
        if attrs["order_type"] == "limit" and not attrs.get("price"):
            raise serializers.ValidationError("Price is required for limit orders.")
        if attrs["order_type"] == "stop" and not attrs.get("stop_price"):
            raise serializers.ValidationError("Stop price is required for stop orders.")
        if attrs.get("quantity", 0) <= 0:
            raise serializers.ValidationError("Quantity must be positive.")
        return attrs


class HoldingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Holding
        fields = ["id", "symbol", "quantity", "avg_entry_price", "created_at", "updated_at"]
        read_only_fields = fields


class OrderCancelSerializer(serializers.Serializer):
    pass
