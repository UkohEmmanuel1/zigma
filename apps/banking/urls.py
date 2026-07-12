from django.urls import path

from banking.views import (
    BankAccountCreateView,
    BankAccountDetailView,
    BankTransactionListView,
    BillPayView,
    ExternalTransferView,
    P2PTransferView,
)

app_name = "banking"

urlpatterns = [
    path("account/", BankAccountCreateView.as_view(), name="banking-account-create"),
    path("account/detail/", BankAccountDetailView.as_view(), name="banking-account-detail"),
    path("transactions/", BankTransactionListView.as_view(), name="banking-transactions"),
    path("transfer/", ExternalTransferView.as_view(), name="banking-transfer"),
    path("p2p/", P2PTransferView.as_view(), name="banking-p2p"),
    path("billpay/", BillPayView.as_view(), name="banking-billpay"),
]
