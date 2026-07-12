import time

import redis
from django.conf import settings
from django.db import connection
from django.db.utils import OperationalError
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        start = time.time()

        db_ok = self._check_database()
        redis_ok = self._check_redis()

        overall = "healthy" if (db_ok and redis_ok) else "degraded"
        http_status = status.HTTP_200_OK if overall == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE

        return Response({
            "status": overall,
            "version": getattr(settings, "APP_VERSION", "2.0.0"),
            "checks": {
                "database": "ok" if db_ok else "fail",
                "redis": "ok" if redis_ok else "fail",
            },
            "response_time_ms": round((time.time() - start) * 1000, 2),
        }, status=http_status)

    def _check_database(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        except OperationalError:
            return False

    def _check_redis(self):
        try:
            r = redis.from_url(settings.CELERY_BROKER_URL, socket_timeout=3)
            r.ping()
            return True
        except redis.ConnectionError:
            return False
