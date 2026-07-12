import random

from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from cards.models import BankCard
from cards.serializers import (
    BankCardCreateSerializer,
    BankCardSerializer,
    CardLimitSerializer,
    CardToggleSerializer,
)


class BankCardCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = BankCardCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        brand = serializer.validated_data["brand"]
        last4 = str(random.randint(1000, 9999))

        card = BankCard.objects.create(
            user=request.user,
            provider="STRIPE_ISSUING",
            provider_card_id=f"ic_{random.randint(100000, 999999)}",
            last4=last4,
            expiry_month=12,
            expiry_year=2029,
            brand=brand,
        )

        out = BankCardSerializer(card)
        return Response(out.data, status=status.HTTP_201_CREATED)


class BankCardListView(ListAPIView):
    serializer_class = BankCardSerializer

    def get_queryset(self):
        return BankCard.objects.filter(user=self.request.user)


class BankCardDetailView(RetrieveAPIView):
    serializer_class = BankCardSerializer

    def get_queryset(self):
        return BankCard.objects.filter(user=self.request.user)


class BankCardFreezeView(APIView):
    def post(self, request, pk):
        return self._update_status(pk, request.user, "FROZEN")


class BankCardUnfreezeView(APIView):
    def post(self, request, pk):
        return self._update_status(pk, request.user, "ACTIVE")


class BankCardCancelView(APIView):
    def post(self, request, pk):
        return self._update_status(pk, request.user, "CANCELLED")

    def _update_status(self, pk, user, new_status):
        try:
            card = BankCard.objects.get(pk=pk, user=user)
        except BankCard.DoesNotExist:
            return Response(
                {"detail": "Card not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        card.status = new_status
        card.save(update_fields=["status"])
        return Response(BankCardSerializer(card).data)


class BankCardLimitView(APIView):
    def post(self, request, pk):
        try:
            card = BankCard.objects.get(pk=pk, user=request.user)
        except BankCard.DoesNotExist:
            return Response(
                {"detail": "Card not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CardLimitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if "daily_limit_cents" in serializer.validated_data:
            card.daily_limit_cents = serializer.validated_data["daily_limit_cents"]
        if "monthly_limit_cents" in serializer.validated_data:
            card.monthly_limit_cents = serializer.validated_data["monthly_limit_cents"]
        card.save()

        return Response(BankCardSerializer(card).data)


class BankCardToggleOnlineView(APIView):
    def post(self, request, pk):
        return self._toggle(pk, request.user, "online_enabled")


class BankCardToggleAtmView(APIView):
    def post(self, request, pk):
        return self._toggle(pk, request.user, "atm_enabled")

    def _toggle(self, pk, user, field):
        try:
            card = BankCard.objects.get(pk=pk, user=user)
        except BankCard.DoesNotExist:
            return Response(
                {"detail": "Card not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CardToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        setattr(card, field, serializer.validated_data["enabled"])
        card.save(update_fields=[field])

        return Response(BankCardSerializer(card).data)
