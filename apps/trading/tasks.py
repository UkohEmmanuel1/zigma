import logging

from celery import shared_task

from market_data.models import MarketQuote
from trading.models import Order
from trading.services import execute_market_order, get_current_price

logger = logging.getLogger(__name__)


@shared_task
def match_limit_orders():
    pending = Order.objects.filter(status="pending", order_type__in=["limit", "stop"])
    matched = 0

    for order in pending:
        current_price = get_current_price(order.symbol)
        if current_price is None:
            continue

        should_execute = False
        fill_price = current_price

        if order.order_type == "limit":
            limit_price = float(order.price)
            if order.side == "buy" and current_price <= limit_price:
                should_execute = True
                fill_price = current_price
            elif order.side == "sell" and current_price >= limit_price:
                should_execute = True
                fill_price = current_price

        elif order.order_type == "stop":
            stop_price = float(order.stop_price)
            if order.side == "buy" and current_price >= stop_price:
                should_execute = True
                fill_price = current_price
            elif order.side == "sell" and current_price <= stop_price:
                should_execute = True
                fill_price = current_price

        if should_execute:
            success = execute_market_order(order, fill_price)
            if success:
                matched += 1
                logger.info("Matched order %s at %.2f", order.id, fill_price)
            else:
                logger.warning("Failed to match order %s", order.id)

    logger.info("match_limit_orders: matched %d / %d pending", matched, pending.count())
    return matched
