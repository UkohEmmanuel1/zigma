from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from kyc.models import KYCVerification
from kyc.serializers import KYCStatusSerializer, KYCUploadSerializer


class KYCUploadView(GenericAPIView):
    serializer_class = KYCUploadSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        kyc = serializer.save()
        out = KYCStatusSerializer(kyc)
        return Response(out.data, status=status.HTTP_200_OK)


class KYCStatusView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            kyc = KYCVerification.objects.get(user=request.user)
        except KYCVerification.DoesNotExist:
            return Response({"status": "NOT_STARTED", "detail": "No KYC submission found."})
        out = KYCStatusSerializer(kyc)
        return Response(out.data)
