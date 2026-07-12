from django.urls import path

from ai_engine.views import (
    MessageCreateView,
    MessageListView,
    PortfolioAnalyzeView,
    SessionCreateView,
    SessionDetailView,
    SessionListView,
    StockInsightView,
)

app_name = "ai_engine"

urlpatterns = [
    path("chat/sessions/", SessionListView.as_view(), name="ai-session-list"),
    path("chat/sessions/create/", SessionCreateView.as_view(), name="ai-session-create"),
    path("chat/sessions/<uuid:pk>/", SessionDetailView.as_view(), name="ai-session-detail"),
    path("chat/sessions/<uuid:pk>/messages/", MessageListView.as_view(), name="ai-message-list"),
    path("chat/sessions/<uuid:pk>/messages/create/", MessageCreateView.as_view(), name="ai-message-create"),
    path("portfolio/analyze/", PortfolioAnalyzeView.as_view(), name="ai-portfolio-analyze"),
    path("stock/insight/<str:market_type>/<str:symbol>/", StockInsightView.as_view(), name="ai-stock-insight"),
]
