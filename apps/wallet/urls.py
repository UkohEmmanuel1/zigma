from django.urls import path

from wallet.views import DepositView, TransactionListView, WalletDetailView

app_name = "wallet"

urlpatterns = [
    path("", WalletDetailView.as_view(), name="wallet-detail"),
    path("deposit/", DepositView.as_view(), name="wallet-deposit"),
    path("transactions/", TransactionListView.as_view(), name="wallet-transactions"),
]
