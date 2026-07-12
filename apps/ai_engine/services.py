import logging
import os

import google.generativeai as genai
from django.conf import settings

from market_data.models import MarketQuote
from portfolio.models import Portfolio, PortfolioHolding
from trading.models import Order

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are Zigma, an AI trading assistant for a paper trading platform.
You help users understand their portfolio, explain market concepts, and analyze trading activity.
Provide clear, concise answers. When discussing prices, use the data provided in context.
Do not give personalized financial advice — remind users this is a paper trading simulation."""

ANALYSIS_PROMPT = """You are Zigma, an AI portfolio analyst.
Analyze the following portfolio data and provide a concise summary including:
1. Overall portfolio health and diversification
2. Best and worst performing positions
3. Cash allocation vs invested
4. Suggestions for consideration (reminding this is paper trading)


Portfolio Data:
"""


def get_gemini_client():
    api_key = getattr(settings, "GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.0-flash")


def build_portfolio_context(user):
    try:
        portfolio = Portfolio.objects.get(user=user)
    except Portfolio.DoesNotExist:
        return "No portfolio found."

    lines = [f"Cash Balance: ${float(portfolio.cash_balance):.2f}"]
    holdings = PortfolioHolding.objects.filter(portfolio=portfolio)

    for h in holdings:
        try:
            quote = MarketQuote.objects.get(symbol=h.symbol)
            price = float(quote.last) if quote.last else 0
        except MarketQuote.DoesNotExist:
            price = 0
        mv = float(h.quantity) * price
        pl = (price - float(h.avg_entry_price)) * float(h.quantity)
        lines.append(
            f"{h.symbol}: {float(h.quantity):.4f} shares @ ${float(h.avg_entry_price):.2f} "
            f"| Current: ${price:.2f} | Value: ${mv:.2f} | P&L: ${pl:.2f}"
        )

    recent_orders = Order.objects.filter(user=user, status__in=["filled", "rejected"]).order_by("-created_at")[:5]
    if recent_orders:
        lines.append("\nRecent Orders:")
        for o in recent_orders:
            lines.append(f"  {o.side.title()} {o.quantity} {o.symbol} ({o.order_type}) — {o.status}")

    return "\n".join(lines)


def call_gemini(system_prompt, user_message, context=None):
    model = get_gemini_client()
    parts = [system_prompt]
    if context:
        parts.append(f"\n--- User Context ---\n{context}")
    parts.append(f"\n--- User Message ---\n{user_message}")
    response = model.generate_content("\n".join(parts))
    return response.text


def generate_portfolio_analysis(user):
    context = build_portfolio_context(user)
    model = get_gemini_client()
    response = model.generate_content(f"{ANALYSIS_PROMPT}\n{context}")
    return response.text


def get_stock_insight(market_type, symbol):
    try:
        quote = MarketQuote.objects.get(symbol=symbol)
        price = float(quote.last) if quote.last else 0
    except MarketQuote.DoesNotExist:
        price = 0

    context = f"Market Type: {market_type}\nSymbol: {symbol}\nCurrent Price: ${price:.2f}"
    prompt = (
        "You are Zigma, an AI stock analyst. "
        "Provide a concise insight (bull/bear outlook, key levels, and a summary) "
        f"for {symbol} in 3-4 sentences.\n\nData:\n{context}"
    )
    model = get_gemini_client()
    response = model.generate_content(prompt)
    return response.text
