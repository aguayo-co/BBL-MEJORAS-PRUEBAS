"""Configs for Gunicorn Server."""
import os

# pylint: disable=invalid-name
max_requests = os.environ.get("MAX_REQUEST", 800)
max_requests_jitter = os.environ.get("MAX_REQUEST_JITTER", 100)
log_file = "-"
worker_class = os.environ.get("WORKER_CLASS", "sync")
threads = os.environ.get("WEB_THREADS", 1)
preload_app = os.environ.get("PRELOAD") == "True"
