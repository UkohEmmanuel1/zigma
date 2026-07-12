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
    def post(self, request, *args, **kwargs):
        serializer = DepositSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        amount = serializer.validated_data["amount_cents"]

        wallet.balance_cents += amount
        wallet.save(update_fields=["balance_cents"])

        Transaction.objects.create(
            wallet=wallet,
            type="DEPOSIT",
            amount_cents=amount,
            balance_after_cents=wallet.balance_cents,
            reference=f"dep_{wallet.id}_{amount}",
        )

        out = WalletSerializer(wallet)
        return Response(out.data, status=status.HTTP_200_OK)


class TransactionListView(ListAPIView):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        wallet, _ = Wallet.objects.get_or_create(user=self.request.user)
        return Transaction.objects.filter(wallet=wallet)
