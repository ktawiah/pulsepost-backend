import os
from datetime import timedelta

from configurations import Configuration
from decouple import config


class Base(Configuration):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DEVELOPMENT_MODE = config(option="DEVELOPMENT_MODE", cast=bool)

    SECRET_KEY = config(
        option="DJANGO_SECRET_KEY",
    )

    THIRD_PARTY_APPS = [
        "rest_framework",
        "djoser",
        "social_django",
        "corsheaders",
        # "drf_yasg",
        "drf_spectacular",
        "jazzmin",
    ]

    DJANGO_APPS = [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
    ]

    LOCAL_APPS = [
        "apps.accounts",
        "apps.posts",
    ]

    INSTALLED_APPS = THIRD_PARTY_APPS + DJANGO_APPS + LOCAL_APPS

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

    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    CORS_ALLOWED_METHODS = [
        "DELETE",
        "GET",
        "OPTIONS",
        "PATCH",
        "POST",
        "PUT",
    ]
    CORS_ALLOWED_HEADERS = [
        "accept",
        "accept-encoding",
        "authorization",
        "content-type",
        "dnt",
        "origin",
        "user-agent",
        "x-csrftoken",
        "x-requested-with",
    ]

    # CSRF settings
    CSRF_TRUSTED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    CSRF_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_HTTPONLY = False
    CSRF_COOKIE_SECURE = False  # Set to True in production with HTTPS

    ROOT_URLCONF = "core.urls"

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ]

    WSGI_APPLICATION = "core.wsgi.application"

    AUTH_USER_MODEL = "user_accounts.User"

    AUTH_PASSWORD_VALIDATORS = [
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
        },
    ]

    LANGUAGE_CODE = "en-us"

    TIME_ZONE = "UTC"

    USE_I18N = True

    USE_TZ = True

    STATIC_URL = "/static/"

    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

    DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

    REST_FRAMEWORK = {
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "apps.accounts.authentication.CustomJWTAuthentication",
        ],
        "DEFAULT_PERMISSION_CLASSES": [
            "rest_framework.permissions.IsAuthenticated",
        ],
        "DEFAULT_RENDERER_CLASSES": [
            "rest_framework.renderers.JSONRenderer",
            "rest_framework.renderers.BrowsableAPIRenderer",
        ],
        "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    }

    AUTH_COOKIE_ACCESS_MAX_AGE = 60 * 60
    AUTH_COOKIE_REFRESH_MAX_AGE = 60 * 60 * 24
    AUTH_COOKIE_SAMESITE = None
    AUTH_COOKIE_HTTPONLY = True
    AUTH_COOKIE_PATH = "/"
    AUTH_COOKIE_SECURE = (
        config(
            option="AUTH_COOKIE_SECURE",
            default="True",
        )
        == "True"
    )

    SIMPLE_JWT = {
        "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
        "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
        "AUTH_HEADER_TYPES": ("Bearer",),
        "ALGORITHM": "HS256",
        "SIGNING_KEY": SECRET_KEY,
        "TOKEN_OBTAIN_SERIALIZER": "apps.accounts.api.serializers.CustomTokenObtainPairSerializer",
    }

    DJOSER = {
        "SERIALIZERS": {
            "user": "apps.accounts.api.serializers.CustomUserSerializer",
            "current_user": "apps.accounts.api.serializers.CustomUserSerializer",
        },
        # "SEND_ACTIVATION_EMAIL": True,
        # "ACTIVATION_URL": "activate/{uid}/{token}",
        "PASSWORD_RESET_CONFIRM_URL": "password-reset/{uid}/{token}",
        "USER_CREATE_PASSWORD_RETYPE": True,
        "LOGOUT_ON_PASSWORD_CHANGE": True,
        "TOKEN_MODEL": None,
        "SET_PASSWORD_RETYPE": True,
        "PASSWORD_RESET_CONFIRM_RETYPE": True,
        "SOCIAL_AUTH_ALLOWED_REDIRECT_URIS": config("SOCIAL_AUTH_ALLOWED_REDIRECT_URIS").split(","),
    }

    AUTHENTICATION_BACKENDS = (
        "social_core.backends.google.GoogleOAuth2",
        "social_core.backends.github.GithubOAuth2",
        "django.contrib.auth.backends.ModelBackend",
    )

    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = config("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY")
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = config("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET")
    SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
        "email",
        "openid",
        "profile",
    ]

    SOCIAL_AUTH_GITHUB_KEY = config("SOCIAL_AUTH_GITHUB_KEY")
    SOCIAL_AUTH_GITHUB_SECRET = config("SOCIAL_AUTH_GITHUB_SECRET")
    SOCIAL_AUTH_GITHUB_SCOPE = [
        "user:email",
        "user",
    ]

    EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
    DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL")
    SENDGRID_API_KEY = config("SENDGRID_API_KEY")
    SENDGRID_SANDBOX_MODE_IN_DEBUG = False

    SPECTACULAR_SETTINGS = {
        "TITLE": "PulsePost API",
        "DESCRIPTION": "PulsePost REST API Documentation.",
        "VERSION": "1.0.0",
        "SERVE_INCLUDE_SCHEMA": False,
        "CONTACT": {
            "name": "Kelvin Tawiah",
            "email": "kelvintawiah224@gmail.com",
            "url": "https://kelvintawiahdev.vercel.app",
        },
    }
