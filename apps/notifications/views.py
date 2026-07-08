from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.models import Notification
from notifications.serializers import MarkReadSerializer, NotificationSerializer


class NotificationListView(ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user)
        unread_only = self.request.query_params.get("unread_only")
        if unread_only and unread_only.lower() == "true":
            qs = qs.filter(is_read=False)
        return qs.order_by("-created_at")


class MarkReadView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = MarkReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        qs = Notification.objects.filter(user=request.user)

        if serializer.validated_data.get("all"):
            count = qs.filter(is_read=False).update(is_read=True)
        elif serializer.validated_data.get("ids"):
            count = qs.filter(id__in=serializer.validated_data["ids"]).update(is_read=True)
        else:
            return Response(
                {"detail": "Provide 'ids' or set 'all' to true."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"marked_read": count})
