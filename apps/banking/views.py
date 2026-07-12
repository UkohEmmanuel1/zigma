import random

from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from banking.models import BankAccount, BankTransaction
from banking.serializers import (
    BankAccountCreateSerializer,
    BankAccountSerializer,
    BankTransactionSerializer,
    BillPaySerializer,
    ExternalTransferSerializer,
    P2PSerializer,
)
from users.models import User
from wallet.models import P2PTransfer
from wallet.serializers import P2PTransferSerializer


class BankAccountCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = BankAccountCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if BankAccount.objects.filter(user=request.user).exists():
            return Response(
                {"detail": "User already has a bank account."},
                status=status.HTTP_409_CONFLICT,
            )

        account = BankAccount.objects.create(
            user=request.user,
            account_number=str(random.randint(1000000000, 9999999999)),
            routing_number="021000021",
            provider=serializer.validated_data.get("provider", "STRIPE"),
            provider_account_id=f"prov_{random.randint(100000, 999999)}",
        )

        out = BankAccountSerializer(account)
        return Response(out.data, status=status.HTTP_201_CREATED)


class BankAccountDetailView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            account = BankAccount.objects.get(user=request.user)
        except BankAccount.DoesNotExist:
            return Response(
                {"detail": "No bank account found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        out = BankAccountSerializer(account)
        return Response(out.data)


class BankTransactionListView(ListAPIView):
    serializer_class = BankTransactionSerializer

    def get_queryset(self):
        try:
            account = BankAccount.objects.get(user=self.request.user)
        except BankAccount.DoesNotExist:
            return BankTransaction.objects.none()
        return BankTransaction.objects.filter(account=account)


class ExternalTransferView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ExternalTransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            account = BankAccount.objects.get(user=request.user)
        except BankAccount.DoesNotExist:
            return Response(
                {"detail": "No bank account found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        amount = serializer.validated_data["amount_cents"]
        if account.balance_cents < amount:
            return Response(
                {"error": {"code": "INSUFFICIENT_FUNDS", "message": "You do not have enough balance."}},
                status=status.HTTP_409_CONFLICT,
            )

        account.balance_cents -= amount
        account.save(update_fields=["balance_cents"])

        BankTransaction.objects.create(
            account=account,
            type="TRANSFER_OUT",
            amount_cents=amount,
            balance_after_cents=account.balance_cents,
            description=f"Transfer to {serializer.validated_data['recipient_account_number']}",
        )

        return Response({"detail": "Transfer initiated.", "amount_cents": amount})


class P2PTransferView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = P2PSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            recipient = User.objects.get(email=serializer.validated_data["recipient_email"])
        except User.DoesNotExist:
            return Response(
                {"detail": "Recipient not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if recipient == request.user:
            return Response(
                {"detail": "Cannot send to yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        amount = serializer.validated_data["amount_cents"]
        note = serializer.validated_data.get("note", "")

        transfer = P2PTransfer.objects.create(
            sender=request.user,
            recipient=recipient,
            amount_cents=amount,
            note=note,
        )

        out = P2PTransferSerializer(transfer)
        return Response(out.data, status=status.HTTP_201_CREATED)


class BillPayView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = BillPaySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"detail": "Bill pay is not yet available.", "status": "coming_soon"},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )
