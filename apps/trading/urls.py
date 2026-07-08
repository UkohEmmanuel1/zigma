from django.urls import path

from trading.views import HoldingListView, OrderCancelView, OrderCreateView, OrderListView

app_name = "trading"

urlpatterns = [
    path("orders/", OrderCreateView.as_view(), name="order-create"),
    path("orders/list/", OrderListView.as_view(), name="order-list"),
    path("orders/<uuid:pk>/cancel/", OrderCancelView.as_view(), name="order-cancel"),
    path("holdings/", HoldingListView.as_view(), name="holding-list"),
]
