from rest_framework.generics import ListAPIView, RetrieveAPIView

from portfolio.models import Portfolio, PortfolioSnapshot
from portfolio.serializers import PortfolioPerformanceSerializer, PortfolioSerializer


class PortfolioView(RetrieveAPIView):
    serializer_class = PortfolioSerializer

    def get_object(self):
        portfolio, _ = Portfolio.objects.get_or_create(user=self.request.user)
        return portfolio


class PortfolioPerformanceView(ListAPIView):
    serializer_class = PortfolioPerformanceSerializer

    def get_queryset(self):
        portfolio, _ = Portfolio.objects.get_or_create(user=self.request.user)
        qs = PortfolioSnapshot.objects.filter(portfolio=portfolio)

        start = self.request.query_params.get("start_date")
        if start:
            qs = qs.filter(snapshot_date__gte=start)

        end = self.request.query_params.get("end_date")
        if end:
            qs = qs.filter(snapshot_date__lte=end)

        return qs
