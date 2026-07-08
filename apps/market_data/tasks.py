import logging

import requests
from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from market_data.models import MarketQuote, PriceHistory, WatchedSymbol

logger = logging.getLogger(__name__)


@shared_task
def fetch_market_data():
    symbols = list(
        WatchedSymbol.objects.filter(is_active=True).values_list("symbol", flat=True)
    )
    if not symbols:
        logger.warning("No active watched symbols configured")
        return

    url = settings.APCA_BASE_URL + "/v2/stocks/quotes/latest"
    headers = {
        "APCA-API-KEY-ID": settings.APCA_API_KEY_ID,
        "APCA-API-SECRET-KEY": settings.APCA_API_SECRET_KEY,
    }
    params = {"symbols": ",".join(symbols)}

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        logger.error("Failed to fetch market data: %s", e)
        return

    now = timezone.now()
    for symbol, quote in data.get("quotes", {}).items():
        try:
            with transaction.atomic():
                MarketQuote.objects.update_or_create(
                    symbol=symbol,
                    defaults={
                        "bid": quote.get("bp"),
                        "ask": quote.get("ap"),
                        "last": quote.get("c"),
                        "volume": None,
                        "timestamp": now,
                    },
                )
            logger.debug("Updated quote for %s", symbol)
        except Exception as e:
            logger.error("Failed to upsert quote for %s: %s", symbol, e)


@shared_task
def fetch_price_history():
    symbols = list(
        WatchedSymbol.objects.filter(is_active=True).values_list("symbol", flat=True)
    )
    if not symbols:
        logger.warning("No active watched symbols configured")
        return

    url = settings.APCA_BASE_URL + "/v2/stocks/bars/latest"
    headers = {
        "APCA-API-KEY-ID": settings.APCA_API_KEY_ID,
        "APCA-API-SECRET-KEY": settings.APCA_API_SECRET_KEY,
    }
    params = {"symbols": ",".join(symbols), "feed": "iex"}

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        logger.error("Failed to fetch price history: %s", e)
        return

    interval = "1Min"
    for symbol, bar in data.get("bars", {}).items():
        try:
            with transaction.atomic():
                PriceHistory.objects.update_or_create(
                    symbol=symbol,
                    interval=interval,
                    timestamp=bar.get("t"),
                    defaults={
                        "open": bar.get("o"),
                        "high": bar.get("h"),
                        "low": bar.get("l"),
                        "close": bar.get("c"),
                        "volume": bar.get("v"),
                    },
                )
            logger.debug("Updated price history for %s", symbol)
        except Exception as e:
            logger.error("Failed to upsert price history for %s: %s", symbol, e)
