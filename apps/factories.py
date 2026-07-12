import factory
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save

from banking.models import BankAccount, BankTransaction
from cards.models import BankCard
from crypto.models import CryptoHolding, CryptoOrder, CryptoWallet, CryptoSwa
from market_data.models import MarketQuote
from notifications.models import Notification
from portfolio.models import Portfolio, PortfolioHolding, PortfolioSnapshot
from trading.models import Holding, Order
from wallet.models import P2PTransfer, Transaction, Wallet

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@zigma.io")
    password = factory.PostGenerationMethodCall("set_password", "TestPass123!")
    is_active = True


class WalletFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Wallet

    user = factory.SubFactory(UserFactory)
    balance_cents = 100000
    currency = "USD"


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction

    wallet = factory.SubFactory(WalletFactory)
    type = "DEPOSIT"
    amount_cents = 50000
    balance_after_cents = 150000


class P2PTransferFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = P2PTransfer

    sender = factory.SubFactory(UserFactory)
    recipient = factory.SubFactory(UserFactory)
    amount_cents = 10000
    status = "COMPLETED"


class CryptoWalletFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CryptoWallet

    user = factory.SubFactory(UserFactory)
    currency = "BTC"
    balance = 1.0


class CryptoOrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CryptoOrder

    user = factory.SubFactory(UserFactory)
    symbol = "BTCUSD"
    side = "BUY"
    order_type = "MARKET"
    quantity = 0.1
    status = "PENDING"
    is_paper = True


class CryptoHoldingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CryptoHolding

    user = factory.SubFactory(UserFactory)
    symbol = "BTC"
    quantity = 0.5
    avg_entry_price = 50000


class CryptoSwaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CryptoSwa

    user = factory.SubFactory(UserFactory)
    from_currency = "BTC"
    to_currency = "ETH"
    from_amount = 0.1
    status = "PENDING"
    is_paper = True


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)
    symbol = "AAPL"
    side = "buy"
    order_type = "market"
    quantity = 10
    status = "pending"


class HoldingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Holding

    user = factory.SubFactory(UserFactory)
    symbol = "AAPL"
    quantity = 100
    avg_entry_price = 150.00


class PortfolioFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Portfolio

    user = factory.SubFactory(UserFactory)
    cash_balance = 50000.00


class PortfolioHoldingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PortfolioHolding

    portfolio = factory.SubFactory(PortfolioFactory)
    symbol = "AAPL"
    quantity = 10
    avg_entry_price = 150.00


class PortfolioSnapshotFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PortfolioSnapshot

    portfolio = factory.SubFactory(PortfolioFactory)
    total_value = 55000.00
    cash_balance = 50000.00


class MarketQuoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MarketQuote

    symbol = "AAPL"
    last = 175.00
    bid = 174.50
    ask = 175.50
    volume = 1000000


class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notification

    user = factory.SubFactory(UserFactory)
    type = "order_filled"
    title = "Order Filled"
    message = "Your AAPL order has been filled."
    is_read = False


class BankAccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BankAccount

    user = factory.SubFactory(UserFactory)
    account_number = factory.Sequence(lambda n: f"{n:010d}")
    routing_number = "021000021"
    provider = "STRIPE"
    balance_cents = 500000
    status = "ACTIVE"


class BankTransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BankTransaction

    account = factory.SubFactory(BankAccountFactory)
    type = "DEPOSIT"
    amount_cents = 100000
    balance_after_cents = 600000


class BankCardFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BankCard

    user = factory.SubFactory(UserFactory)
    provider = "STRIPE_ISSUING"
    provider_card_id = factory.Sequence(lambda n: f"ic_{n:06d}")
    last4 = factory.Sequence(lambda n: f"{n:04d}"[-4:])
    expiry_month = 12
    expiry_year = 2029
    brand = "VISA"
    status = "ACTIVE"
