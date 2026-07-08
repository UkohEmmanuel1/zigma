from rest_framework import serializers

from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "type", "title", "message", "related_object_type",
                   "related_object_id", "is_read", "created_at"]
        read_only_fields = fields


class MarkReadSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.UUIDField(), required=False)
    all = serializers.BooleanField(default=False)
