import random
from decimal import Decimal

from django.db import transaction
from django.db.models import F

from crypto.models import CryptoHolding, CryptoWallet
from wallet.models import Transaction, Wallet


SUPPORTED_CRYPTO = {"BTC", "ETH", "SOL", "XRP", "ADA", "DOT", "AVAX", "MATIC", "LINK", "UNI"}

BASE_RATES_USD = {
    "BTC": Decimal("67500.00"),
    "ETH": Decimal("3450.00"),
    "SOL": Decimal("145.00"),
    "XRP": Decimal("0.62"),
    "ADA": Decimal("0.45"),
    "DOT": Decimal("7.20"),
    "AVAX": Decimal("35.80"),
    "MATIC": Decimal("0.72"),
    "LINK": Decimal("14.50"),
    "UNI": Decimal("9.80"),
}


def get_crypto_rate(from_currency, to_currency):
    if from_currency == "USD" and to_currency in BASE_RATES_USD:
        return Decimal(1) / BASE_RATES_USD[to_currency]
    if to_currency == "USD" and from_currency in BASE_RATES_USD:
        return BASE_RATES_USD[from_currency]
    if from_currency in BASE_RATES_USD and to_currency in BASE_RATES_USD:
        return BASE_RATES_USD[from_currency] / BASE_RATES_USD[to_currency]
    jitter = Decimal(str(random.uniform(0.95, 1.05)))
    return Decimal(str(random.uniform(0.5, 50000))) * jitter


@transaction.atomic
def execute_buy(user, from_currency, to_currency, amount_cents):
    if from_currency != "USD":
        raise ValueError("Only USD is supported as the source currency for buys.")

    wallet = Wallet.objects.select_for_update().get(user=user)
    if wallet.balance_cents < amount_cents:
        raise ValueError("Insufficient fiat balance.")

    rate = get_crypto_rate("USD", to_currency)
    crypto_amount = Decimal(amount_cents) / 100 * rate

    wallet.balance_cents -= amount_cents
    wallet.save(update_fields=["balance_cents"])

    crypto_wallet, _ = CryptoWallet.objects.select_for_update().get_or_create(
        user=user, currency=to_currency,
    )
    crypto_wallet.balance += crypto_amount
    crypto_wallet.save(update_fields=["balance"])

    holding, _ = CryptoHolding.objects.select_for_update().get_or_create(
        user=user, symbol=to_currency,
    )
    total_cost = Decimal(amount_cents) / 100
    new_qty = holding.quantity + crypto_amount
    holding.avg_entry_price = (
        (holding.avg_entry_price * holding.quantity + total_cost) / new_qty
        if holding.quantity > 0 else Decimal(amount_cents) / 100 / crypto_amount
    )
    holding.quantity = new_qty
    holding.save()

    Transaction.objects.create(
        wallet=wallet,
        type="CRYPTO_BUY",
        amount_cents=-amount_cents,
        balance_after_cents=wallet.balance_cents,
        description=f"Bought {crypto_amount:.8f} {to_currency}",
        metadata={
            "crypto_currency": to_currency,
            "crypto_amount": str(crypto_amount),
            "rate": str(rate),
        },
    )

    return {
        "from_currency": from_currency,
        "to_currency": to_currency,
        "spent_cents": amount_cents,
        "crypto_amount": crypto_amount,
        "rate": rate,
        "balance_cents": wallet.balance_cents,
    }


@transaction.atomic
def execute_sell(user, from_currency, to_currency, quantity):
    if to_currency != "USD":
        raise ValueError("Only USD is supported as the target currency for sells.")

    holding = CryptoHolding.objects.select_for_update().get(
        user=user, symbol=from_currency,
    )
    if holding.quantity < quantity:
        raise ValueError("Insufficient crypto balance.")

    rate = get_crypto_rate(from_currency, "USD")
    usd_amount_cents = int(quantity * rate * 100)

    holding.quantity -= quantity
    if holding.quantity <= 0:
        holding.delete()
    else:
        holding.save(update_fields=["quantity"])

    crypto_wallet, _ = CryptoWallet.objects.select_for_update().get_or_create(
        user=user, currency=from_currency,
    )
    crypto_wallet.balance -= quantity
    if crypto_wallet.balance < 0:
        crypto_wallet.balance = 0
    crypto_wallet.save(update_fields=["balance"])

    wallet = Wallet.objects.select_for_update().get(user=user)
    wallet.balance_cents += usd_amount_cents
    wallet.save(update_fields=["balance_cents"])

    Transaction.objects.create(
        wallet=wallet,
        type="CRYPTO_SELL",
        amount_cents=usd_amount_cents,
        balance_after_cents=wallet.balance_cents,
        description=f"Sold {quantity:.8f} {from_currency}",
        metadata={
            "crypto_currency": from_currency,
            "crypto_amount": str(quantity),
            "rate": str(rate),
        },
    )

    return {
        "from_currency": from_currency,
        "to_currency": to_currency,
        "quantity": quantity,
        "received_cents": usd_amount_cents,
        "rate": rate,
        "balance_cents": wallet.balance_cents,
    }
