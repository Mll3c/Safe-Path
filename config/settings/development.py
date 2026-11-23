from datetime import timedelta

from .base import *

DEBUG = True
CORS_ALLOW_ALL_ORIGINS = True

# Long-lived access tokens so manual testing isn't interrupted every few
# minutes. Development only: production keeps the short lifetime from base.
SIMPLE_JWT = {
    **SIMPLE_JWT,
    "ACCESS_TOKEN_LIFETIME": timedelta(days=30),
}
