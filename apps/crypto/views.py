import random
from decimal import Decimal

from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from crypto.models import CryptoHolding, CryptoOrder, CryptoSwa, CryptoWallet
from crypto.serializers import (
    CryptoBuySerializer,
    CryptoHoldingSerializer,
    CryptoOrderCreateSerializer,
    CryptoOrderSerializer,
    CryptoSellSerializer,
    CryptoSwaCreateSerializer,
    CryptoSwaSerializer,
    CryptoWalletSerializer,
)
from crypto.services import execute_buy, execute_sell


class CryptoWalletListView(ListAPIView):
    serializer_class = CryptoWalletSerializer

    def get_queryset(self):
        return CryptoWallet.objects.filter(user=self.request.user)


class CryptoOrderCreateView(CreateAPIView):
    serializer_class = CryptoOrderCreateSerializer

    def perform_create(self, serializer):
        order = serializer.save(user=self.request.user)
        if order.order_type == "MARKET":
            price = Decimal(str(random.uniform(50000, 60000)))
            order.filled_quantity = order.quantity
            order.status = "FILLED"
            order.save(update_fields=["filled_quantity", "status"])

            holding, _ = CryptoHolding.objects.get_or_create(
                user=self.request.user,
                symbol=order.symbol,
            )
            if order.side == "BUY":
                total_cost = price * order.quantity
                new_qty = holding.quantity + order.quantity
                holding.avg_entry_price = (
                    (holding.avg_entry_price * holding.quantity + total_cost) / new_qty
                    if holding.quantity > 0 else price
                )
                holding.quantity = new_qty
            else:
                holding.quantity -= order.quantity
                if holding.quantity < 0:
                    holding.quantity = 0
            holding.save()

            CryptoWallet.objects.update_or_create(
                user=self.request.user,
                currency=order.symbol.replace("USD", ""),
                defaults={"balance": 0},
            )


class CryptoOrderListView(ListAPIView):
    serializer_class = CryptoOrderSerializer

    def get_queryset(self):
        qs = CryptoOrder.objects.filter(user=self.request.user)
        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param.upper())
        return qs.order_by("-created_at")


class CryptoOrderDetailView(RetrieveAPIView):
    serializer_class = CryptoOrderSerializer

    def get_queryset(self):
        return CryptoOrder.objects.filter(user=self.request.user)


class CryptoOrderCancelView(APIView):
    def post(self, request, pk):
        try:
            order = CryptoOrder.objects.get(pk=pk, user=request.user)
        except CryptoOrder.DoesNotExist:
            return Response(
                {"detail": "Order not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if order.status != "PENDING":
            return Response(
                {"detail": f"Cannot cancel order in '{order.status}' state."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        order.status = "CANCELLED"
        order.save(update_fields=["status"])
        return Response(CryptoOrderSerializer(order).data)


class CryptoHoldingListView(ListAPIView):
    serializer_class = CryptoHoldingSerializer

    def get_queryset(self):
        return CryptoHolding.objects.filter(user=self.request.user)


class CryptoSwaCreateView(CreateAPIView):
    serializer_class = CryptoSwaCreateSerializer

    def perform_create(self, serializer):
        swap = serializer.save(user=self.request.user)
        rate = Decimal(str(random.uniform(0.05, 0.08)))
        to_amount = swap.from_amount * rate
        swap.rate = rate
        swap.to_amount = to_amount
        swap.status = "COMPLETED"
        swap.save(update_fields=["rate", "to_amount", "status"])

        from_wallet, _ = CryptoWallet.objects.get_or_create(
            user=self.request.user,
            currency=swap.from_currency,
        )
        from_wallet.balance -= swap.from_amount
        if from_wallet.balance < 0:
            from_wallet.balance = 0
        from_wallet.save(update_fields=["balance"])

        to_wallet, _ = CryptoWallet.objects.get_or_create(
            user=self.request.user,
            currency=swap.to_currency,
        )
        to_wallet.balance += to_amount
        to_wallet.save(update_fields=["balance"])


class CryptoSwaListView(ListAPIView):
    serializer_class = CryptoSwaSerializer

    def get_queryset(self):
        return CryptoSwa.objects.filter(user=self.request.user).order_by("-created_at")


class CryptoSwaDetailView(RetrieveAPIView):
    serializer_class = CryptoSwaSerializer

    def get_queryset(self):
        return CryptoSwa.objects.filter(user=self.request.user)


class CryptoSwaCancelView(APIView):
    def post(self, request, pk):
        try:
            swap = CryptoSwa.objects.get(pk=pk, user=request.user)
        except CryptoSwa.DoesNotExist:
            return Response(
                {"detail": "Swap not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if swap.status != "PENDING":
            return Response(
                {"detail": f"Cannot cancel swap in '{swap.status}' state."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        swap.status = "CANCELLED"
        swap.save(update_fields=["status"])
        return Response(CryptoSwaSerializer(swap).data)


class CryptoBuyView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CryptoBuySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = execute_buy(
                user=request.user,
                **serializer.validated_data,
            )
        except ValueError as e:
            return Response(
                {"error": {"code": "INSUFFICIENT_FUNDS", "message": str(e)}},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(result, status=status.HTTP_200_OK)


class CryptoSellView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CryptoSellSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = execute_sell(
                user=request.user,
                **serializer.validated_data,
            )
        except ValueError as e:
            return Response(
                {"error": {"code": "INSUFFICIENT_FUNDS", "message": str(e)}},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(result, status=status.HTTP_200_OK)
