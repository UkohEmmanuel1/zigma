from django.urls import path

from portfolio.views import PortfolioPerformanceView, PortfolioView

app_name = "portfolio"

urlpatterns = [
    path("", PortfolioView.as_view(), name="portfolio"),
    path("performance/", PortfolioPerformanceView.as_view(), name="portfolio-performance"),
]
