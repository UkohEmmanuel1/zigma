from django.urls import path

from crypto.views import (
    CryptoBuyView,
    CryptoHoldingListView,
    CryptoOrderCancelView,
    CryptoOrderCreateView,
    CryptoOrderDetailView,
    CryptoOrderListView,
    CryptoSellView,
    CryptoSwaCancelView,
    CryptoSwaCreateView,
    CryptoSwaDetailView,
    CryptoSwaListView,
    CryptoWalletListView,
)

app_name = "crypto"

urlpatterns = [
    path("wallets/", CryptoWalletListView.as_view(), name="crypto-wallet-list"),
    path("orders/", CryptoOrderListView.as_view(), name="crypto-order-list"),
    path("orders/create/", CryptoOrderCreateView.as_view(), name="crypto-order-create"),
    path("orders/<uuid:pk>/", CryptoOrderDetailView.as_view(), name="crypto-order-detail"),
    path("orders/<uuid:pk>/cancel/", CryptoOrderCancelView.as_view(), name="crypto-order-cancel"),
    path("holdings/", CryptoHoldingListView.as_view(), name="crypto-holding-list"),
    path("buy/", CryptoBuyView.as_view(), name="crypto-buy"),
    path("sell/", CryptoSellView.as_view(), name="crypto-sell"),
    path("swaps/", CryptoSwaListView.as_view(), name="crypto-swap-list"),
    path("swaps/create/", CryptoSwaCreateView.as_view(), name="crypto-swap-create"),
    path("swaps/<uuid:pk>/", CryptoSwaDetailView.as_view(), name="crypto-swap-detail"),
    path("swaps/<uuid:pk>/cancel/", CryptoSwaCancelView.as_view(), name="crypto-swap-cancel"),
]
