import logging

from django.db import transaction
from django.utils import timezone

from market_data.models import MarketQuote
from notifications.services import create_notification
from portfolio.models import Portfolio, PortfolioHolding
from trading.models import Holding, Order

logger = logging.getLogger(__name__)


def get_current_price(symbol):
    try:
        quote = MarketQuote.objects.filter(symbol=symbol).latest("timestamp")
        return float(quote.last) if quote.last else None
    except MarketQuote.DoesNotExist:
        return None


def place_order(user, symbol, side, order_type, quantity, price=None, stop_price=None):
    now = timezone.now()
    order = Order.objects.create(
        user=user,
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price,
        stop_price=stop_price,
        status="pending",
    )

    if order_type == "market":
        fill_price = get_current_price(symbol)
        if fill_price is None:
            order.status = "rejected"
            order.save(update_fields=["status"])
            logger.warning("Order %s rejected: no market price for %s", order.id, symbol)
            create_notification(
                user, "order_rejected",
                message=f"Market order for {quantity} {symbol} rejected: no market price available.",
                related_object_type="order", related_object_id=str(order.id),
            )
            return order
        success = execute_market_order(order, fill_price)
        if not success:
            logger.warning("Order %s failed to execute", order.id)

    return order


def execute_market_order(order, fill_price):
    total_cost = float(order.quantity) * fill_price

    try:
        with transaction.atomic():
            portfolio = Portfolio.objects.select_for_update().get(user=order.user)

            if order.side == "buy":
                if float(portfolio.cash_balance) < total_cost:
                    order.status = "rejected"
                    order.save(update_fields=["status"])
                    logger.warning("Order %s rejected: insufficient funds", order.id)
                    create_notification(
                        order.user, "order_rejected",
                        message=f"Buy {order.quantity} {order.symbol} rejected: insufficient funds (need ${total_cost:.2f}).",
                        related_object_type="order", related_object_id=str(order.id),
                    )
                    return False

                portfolio.cash_balance = float(portfolio.cash_balance) - total_cost
                portfolio.save(update_fields=["cash_balance"])

                holding, created = Holding.objects.get_or_create(
                    user=order.user, symbol=order.symbol,
                    defaults={"quantity": 0, "avg_entry_price": 0},
                )
                old_qty = float(holding.quantity)
                old_avg = float(holding.avg_entry_price)
                new_qty = old_qty + float(order.quantity)
                new_avg = ((old_qty * old_avg) + total_cost) / new_qty
                holding.quantity = new_qty
                holding.avg_entry_price = new_avg
                holding.save()

                ph, _ = PortfolioHolding.objects.get_or_create(
                    portfolio=portfolio, symbol=order.symbol,
                    defaults={"quantity": 0, "avg_entry_price": 0},
                )
                old_pq = float(ph.quantity)
                old_pa = float(ph.avg_entry_price)
                new_pq = old_pq + float(order.quantity)
                new_pa = ((old_pq * old_pa) + total_cost) / new_pq
                ph.quantity = new_pq
                ph.avg_entry_price = new_pa
                ph.save()

            else:
                try:
                    holding = Holding.objects.select_for_update().get(
                        user=order.user, symbol=order.symbol
                    )
                except Holding.DoesNotExist:
                    order.status = "rejected"
                    order.save(update_fields=["status"])
                    logger.warning("Order %s rejected: no holding for %s", order.id, order.symbol)
                    create_notification(
                        order.user, "order_rejected",
                        message=f"Sell {order.quantity} {order.symbol} rejected: no shares held.",
                        related_object_type="order", related_object_id=str(order.id),
                    )
                    return False

                if float(holding.quantity) < float(order.quantity):
                    order.status = "rejected"
                    order.save(update_fields=["status"])
                    logger.warning("Order %s rejected: insufficient shares", order.id)
                    create_notification(
                        order.user, "order_rejected",
                        message=f"Sell {order.quantity} {order.symbol} rejected: only {holding.quantity} shares held.",
                        related_object_type="order", related_object_id=str(order.id),
                    )
                    return False

                portfolio.cash_balance = float(portfolio.cash_balance) + total_cost
                portfolio.save(update_fields=["cash_balance"])

                holding.quantity = float(holding.quantity) - float(order.quantity)
                holding.save()

                try:
                    ph = PortfolioHolding.objects.get(portfolio=portfolio, symbol=order.symbol)
                    ph.quantity = float(ph.quantity) - float(order.quantity)
                    if float(ph.quantity) <= 0:
                        ph.delete()
                    else:
                        ph.save()
                except PortfolioHolding.DoesNotExist:
                    pass

            order.status = "filled"
            order.filled_quantity = order.quantity
            order.save(update_fields=["status", "filled_quantity"])
            logger.info("Order %s filled at %.2f", order.id, fill_price)
            create_notification(
                order.user, "order_filled",
                message=f"{order.side.title()} {order.quantity} {order.symbol} filled at ${fill_price:.2f}.",
                related_object_type="order", related_object_id=str(order.id),
            )
            return True

    except Exception as e:
        logger.error("Failed to execute order %s: %s", order.id, e)
        order.status = "rejected"
        order.save(update_fields=["status"])
        create_notification(
            order.user, "order_rejected",
            message=f"Order {order.symbol} failed due to an internal error.",
            related_object_type="order", related_object_id=str(order.id),
        )
        return False
