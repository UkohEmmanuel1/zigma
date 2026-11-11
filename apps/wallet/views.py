from rest_framework import status
from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from wallet.models import Transaction, Wallet
from wallet.serializers import DepositSerializer, TransactionSerializer, WalletSerializer


class WalletDetailView(RetrieveAPIView):
    serializer_class = WalletSerializer

    def get_object(self):
        wallet, _ = Wallet.objects.get_or_create(user=self.request.user)
        return wallet


class DepositView(APIView):
    """Legacy fiat deposits stay disabled until a provider verifies settlement."""

    def post(self, request, *args, **kwargs):
        return Response(
            {
                "detail": "Deposits are temporarily unavailable. A verified payment provider integration is required before balances can be credited.",
                "code": "DEPOSITS_DISABLED_PENDING_VERIFIED_PROVIDER",
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class TransactionListView(ListAPIView):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        wallet, _ = Wallet.objects.get_or_create(user=self.request.user)
        return Transaction.objects.filter(wallet=wallet)
