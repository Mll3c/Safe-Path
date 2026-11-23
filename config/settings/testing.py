from .base import *

# =============================================================================
# Testing
# =============================================================================

DEBUG = False

# Use a separate Redis logical database for tests.
REDIS_CACHE_URL = "redis://redis:6379/2"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_CACHE_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# Keep Celery isolated from development.
CELERY_BROKER_URL = "redis://redis:6379/3"
CELERY_RESULT_BACKEND = "redis://redis:6379/3"
