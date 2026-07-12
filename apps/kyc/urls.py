from django.urls import path

from kyc.views import KYCStatusView, KYCUploadView

app_name = "kyc"

urlpatterns = [
    path("upload/", KYCUploadView.as_view(), name="kyc-upload"),
    path("status/", KYCStatusView.as_view(), name="kyc-status"),
]
