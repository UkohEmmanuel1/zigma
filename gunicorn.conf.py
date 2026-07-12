import multiprocessing
import os

bind = os.environ.get("GUNICORN_BIND", "0.0.0.0:8000")
workers = os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1)
worker_class = os.environ.get("GUNICORN_WORKER_CLASS", "sync")
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "120"))
graceful_timeout = int(os.environ.get("GUNICORN_GRACEFUL_TIMEOUT", "30"))
keepalive = int(os.environ.get("GUNICORN_KEEPALIVE", "5"))
max_requests = int(os.environ.get("GUNICORN_MAX_REQUESTS", "10000"))
max_requests_jitter = int(os.environ.get("GUNICORN_MAX_REQUESTS_JITTER", "1000"))

accesslog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(L)s'
errorlog = "-"
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")

reload = os.environ.get("GUNICORN_RELOAD", "false").lower() == "true"

preload_app = True

def on_starting(server):
    server.log.info("Starting Zigma API server")

def on_exit(server):
    server.log.info("Shutting down Zigma API server")
