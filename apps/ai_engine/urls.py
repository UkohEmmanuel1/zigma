from django.urls import path

from ai_engine.views import (
    MessageCreateView,
    MessageListView,
    PortfolioAnalyzeView,
    SessionCreateView,
    SessionListView,
)

app_name = "ai_engine"

urlpatterns = [
    path("chat/sessions/", SessionCreateView.as_view(), name="ai-session-create"),
    path("chat/sessions/list/", SessionListView.as_view(), name="ai-session-list"),
    path("chat/sessions/<uuid:pk>/messages/", MessageCreateView.as_view(), name="ai-message-create"),
    path("chat/sessions/<uuid:pk>/messages/list/", MessageListView.as_view(), name="ai-message-list"),
    path("portfolio/analyze/", PortfolioAnalyzeView.as_view(), name="ai-portfolio-analyze"),
]
