from rest_framework import serializers

from ai_engine.models import AIChatSession, AIMessage


class AIChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIChatSession
        fields = ["id", "title", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class AIMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIMessage
        fields = ["id", "role", "content", "metadata", "created_at"]
        read_only_fields = fields


class ChatInputSerializer(serializers.Serializer):
    content = serializers.CharField(min_length=1)
