from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.services import create_notification
from trading.models import Holding, Order
from trading.serializers import (
    HoldingSerializer,
    OrderCreateSerializer,
    OrderSerializer,
)
from trading.services import place_order


class OrderCreateView(CreateAPIView):
    serializer_class = OrderCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = place_order(
            user=request.user,
            **serializer.validated_data,
        )

        out = OrderSerializer(order)
        return Response(out.data, status=status.HTTP_201_CREATED)


class OrderListView(ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        qs = Order.objects.filter(user=self.request.user)
        symbol = self.request.query_params.get("symbol")
        if symbol:
            qs = qs.filter(symbol=symbol.upper())
        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)
        return qs.order_by("-created_at")


class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderCancelView(APIView):
    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {"detail": "Order not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if order.status != "pending":
            return Response(
                {"detail": f"Cannot cancel order in '{order.status}' state."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = "cancelled"
        order.save(update_fields=["status"])
        create_notification(
            request.user, "order_cancelled",
            message=f"{order.side.title()} order for {order.quantity} {order.symbol} cancelled.",
            related_object_type="order", related_object_id=str(order.id),
        )
        return Response(OrderSerializer(order).data)


class HoldingListView(ListAPIView):
    serializer_class = HoldingSerializer

    def get_queryset(self):
        return Holding.objects.filter(user=self.request.user)
