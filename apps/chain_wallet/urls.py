from django.urls import path

from chain_wallet.views import ConnectedWalletDeleteView, ConnectedWalletListCreateView

app_name = "chain_wallet"

urlpatterns = [
    path("", ConnectedWalletListCreateView.as_view(), name="connected-wallet-list-create"),
    path("<uuid:pk>/", ConnectedWalletDeleteView.as_view(), name="connected-wallet-delete"),
]
