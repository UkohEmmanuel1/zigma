import uuid

from django.conf import settings
from django.db import models


class KYCVerification(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUBMITTED", "Submitted"),
        ("IN_REVIEW", "In Review"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="kyc",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    document_type = models.CharField(max_length=50, null=True, blank=True)
    document_front_url = models.URLField(null=True, blank=True)
    document_back_url = models.URLField(null=True, blank=True)
    selfie_url = models.URLField(null=True, blank=True)
    verification_provider = models.CharField(max_length=50, null=True, blank=True)
    provider_reference = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "kyc_verifications"

    def __str__(self):
        return f"{self.user.email} - {self.status}"
