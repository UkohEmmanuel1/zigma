from django.urls import path

from trading.views import (
    HoldingListView,
    OrderCancelView,
    OrderCreateView,
    OrderDetailView,
    OrderListView,
)

app_name = "trading"

urlpatterns = [
    path("orders/", OrderListView.as_view(), name="order-list"),
    path("orders/create/", OrderCreateView.as_view(), name="order-create"),
    path("orders/<uuid:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("orders/<uuid:pk>/cancel/", OrderCancelView.as_view(), name="order-cancel"),
    path("holdings/", HoldingListView.as_view(), name="holding-list"),
]
