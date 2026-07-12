import requests
from django.conf import settings
from rest_framework import status
from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from market_data.models import MarketQuote, PriceHistory
from market_data.serializers import MarketQuoteSerializer, PriceHistorySerializer


class QuoteView(RetrieveAPIView):
    queryset = MarketQuote.objects.all()
    serializer_class = MarketQuoteSerializer
    permission_classes = [AllowAny]
    lookup_field = "symbol"
    lookup_url_kwarg = "symbol"


class MarketQuoteByTypeView(RetrieveAPIView):
    queryset = MarketQuote.objects.all()
    serializer_class = MarketQuoteSerializer
    permission_classes = [AllowAny]
    lookup_field = "symbol"
    lookup_url_kwarg = "symbol"


class CandlesView(ListAPIView):
    serializer_class = PriceHistorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        symbol = self.kwargs["symbol"]
        qs = PriceHistory.objects.filter(symbol=symbol)

        interval = self.request.query_params.get("interval")
        if interval:
            qs = qs.filter(interval=interval)

        start = self.request.query_params.get("start")
        if start:
            qs = qs.filter(timestamp__gte=start)

        end = self.request.query_params.get("end")
        if end:
            qs = qs.filter(timestamp__lte=end)

        qs = qs.order_by("-timestamp")

        limit = self.request.query_params.get("limit")
        if limit:
            try:
                qs = qs[: int(limit)]
            except (ValueError, TypeError):
                pass

        return qs


class SymbolSearchView(GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        query = request.query_params.get("q", "")
        if not query or len(query) < 1:
            return Response({"results": []})

        url = f"{settings.APCA_BASE_URL}/v2/assets"
        headers = {
            "APCA-API-KEY-ID": settings.APCA_API_KEY_ID,
            "APCA-API-SECRET-KEY": settings.APCA_API_SECRET_KEY,
        }
        params = {"search": query}

        try:
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            resp.raise_for_status()
            assets = resp.json()
        except requests.RequestException:
            return Response(
                {"error": "Failed to search symbols"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        results = [
            {"symbol": a["symbol"], "name": a.get("name", ""), "exchange": a.get("exchange", "")}
            for a in assets
            if a.get("tradable")
        ]

        return Response({"results": results})
