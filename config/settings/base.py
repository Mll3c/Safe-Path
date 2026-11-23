from datetime import timedelta
from pathlib import Path

import environ

# =============================================================================
# Environment
# =============================================================================

# Build paths inside the project.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Environment variables are provided by the runtime environment
# (Docker Compose, CI/CD, production server, etc.).
env = environ.Env()


# =============================================================================
# Django Core
# =============================================================================

SECRET_KEY = env("DJANGO_SECRET_KEY")

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =============================================================================
# Applications
# =============================================================================

INSTALLED_APPS = [
    # Django
    "django.contrib.sites",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    # Third-party
    "rest_framework",
    "rest_framework_gis",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_celery_beat",
    "corsheaders",
    # Local
    "apps.core",
    "apps.accounts",
    "apps.groups",
    "apps.trips",
    "apps.geofences",
    "apps.safety",
    "apps.notifications",
    "apps.reports",
]

SITE_ID = 1


# =============================================================================
# Middleware
# =============================================================================

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# =============================================================================
# Templates
# =============================================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# =============================================================================
# Database
# =============================================================================

DATABASES = {
    "default": env.db_url(
        "DATABASE_URL",
        engine="django.contrib.gis.db.backends.postgis",
    )
}


# =============================================================================
# Redis
# =============================================================================

REDIS_CACHE_URL = env("REDIS_CACHE_URL")
CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_CACHE_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}


# =============================================================================
# Django REST Framework
# =============================================================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_PAGINATION_CLASS": ("apps.core.pagination.CustomPageSizePagination"),
    "EXCEPTION_HANDLER": ("apps.core.exception_handlers.custom_exception_handler"),
}


# =============================================================================
# Authentication
# =============================================================================

AUTH_USER_MODEL = "accounts.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]


# =============================================================================
# Password Validation
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": ("django.contrib.auth.password_validation." "MinimumLengthValidator"),
    },
    {
        "NAME": ("django.contrib.auth.password_validation." "CommonPasswordValidator"),
    },
    {
        "NAME": ("django.contrib.auth.password_validation." "NumericPasswordValidator"),
    },
]


# =============================================================================
# Internationalization
# =============================================================================

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"

USE_I18N = True
USE_TZ = True


# =============================================================================
# Static & Media Files
# =============================================================================

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"


# =============================================================================
# Hosts & CORS
# =============================================================================

ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS",
    default=[],
)

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=[],
)


# =============================================================================
# Celery
# =============================================================================

CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"


# =============================================================================
# JWT
# =============================================================================

SIMPLE_JWT = {
    "REFRESH_TOKEN": "refresh_token",
    "ACCESS_TOKEN": "access_token",
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}
