from django.urls import path

from notifications.views import MarkReadView, NotificationListView

app_name = "notifications"

urlpatterns = [
    path("", NotificationListView.as_view(), name="notification-list"),
    path("mark-read/", MarkReadView.as_view(), name="notification-mark-read"),
]
