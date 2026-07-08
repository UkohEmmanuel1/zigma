import logging

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from market_data.models import MarketQuote
from portfolio.models import Portfolio, PortfolioHolding, PortfolioSnapshot

logger = logging.getLogger(__name__)


@shared_task
def take_portfolio_snapshots():
    today = timezone.localdate()
    for portfolio in Portfolio.objects.all():
        holdings = PortfolioHolding.objects.filter(portfolio=portfolio)
        holdings_value = 0
        for holding in holdings:
            try:
                quote = MarketQuote.objects.get(symbol=holding.symbol)
                price = float(quote.last) if quote.last else 0
            except MarketQuote.DoesNotExist:
                price = 0
            holdings_value += float(holding.quantity) * price

        total_value = float(portfolio.cash_balance) + holdings_value

        try:
            with transaction.atomic():
                PortfolioSnapshot.objects.update_or_create(
                    portfolio=portfolio,
                    snapshot_date=today,
                    defaults={
                        "total_value": round(total_value, 2),
                        "cash_balance": portfolio.cash_balance,
                    },
                )
            logger.debug("Snapshot taken for %s", portfolio.user.email)
        except Exception as e:
            logger.error("Failed to snapshot portfolio %s: %s", portfolio.id, e)
