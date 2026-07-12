from django.urls import path

from cards.views import (
    BankCardCancelView,
    BankCardCreateView,
    BankCardDetailView,
    BankCardFreezeView,
    BankCardLimitView,
    BankCardListView,
    BankCardToggleAtmView,
    BankCardToggleOnlineView,
    BankCardUnfreezeView,
)

app_name = "cards"

urlpatterns = [
    path("", BankCardListView.as_view(), name="card-list"),
    path("create/", BankCardCreateView.as_view(), name="card-create"),
    path("<uuid:pk>/", BankCardDetailView.as_view(), name="card-detail"),
    path("<uuid:pk>/freeze/", BankCardFreezeView.as_view(), name="card-freeze"),
    path("<uuid:pk>/unfreeze/", BankCardUnfreezeView.as_view(), name="card-unfreeze"),
    path("<uuid:pk>/limits/", BankCardLimitView.as_view(), name="card-limits"),
    path("<uuid:pk>/toggle/online/", BankCardToggleOnlineView.as_view(), name="card-toggle-online"),
    path("<uuid:pk>/toggle/atm/", BankCardToggleAtmView.as_view(), name="card-toggle-atm"),
    path("<uuid:pk>/cancel/", BankCardCancelView.as_view(), name="card-cancel"),
]
