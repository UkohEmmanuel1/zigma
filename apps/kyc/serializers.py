from rest_framework import serializers

from kyc.models import KYCVerification


class KYCStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCVerification
        fields = ["id", "status", "document_type", "created_at", "updated_at"]
        read_only_fields = fields


class KYCUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCVerification
        fields = ["document_type", "document_front_url", "document_back_url", "selfie_url"]

    def create(self, validated_data):
        user = self.context["request"].user
        kyc, _ = KYCVerification.objects.get_or_create(user=user)
        for attr, value in validated_data.items():
            setattr(kyc, attr, value)
        kyc.status = "SUBMITTED"
        kyc.save()
        return kyc
