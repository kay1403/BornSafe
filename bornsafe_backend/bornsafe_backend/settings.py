"""
Django settings for bornsafe_backend project.
Version finale - Corrigée et optimisée.
"""

from pathlib import Path
from datetime import timedelta
import os
import environ
import sys
from django.contrib.messages import constants as messages

# ----------------------------
# BASE DIR & ENVIRONNEMENT
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    SESSION_COOKIE_SECURE=(bool, False),
    CSRF_COOKIE_SECURE=(bool, False),
    SECURE_SSL_REDIRECT=(bool, False),
)

# Lire le fichier .env (priorité au fichier à la racine)
env_file = os.path.join(BASE_DIR.parent, '.env')
if os.path.exists(env_file):
    environ.Env.read_env(env_file)
else:
    environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# ----------------------------
# SÉCURITÉ DE BASE
# ----------------------------
SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# ----------------------------
# CONFIGURATION DES SESSIONS (CORRIGÉE)
# ----------------------------
# En local (DEBUG=True), on désactive la sécurité SSL
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=not DEBUG)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=not DEBUG)
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=not DEBUG)

CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 semaines
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# ----------------------------
# SÉCURITÉ HTTP
# ----------------------------
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

if not DEBUG:
    SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# ----------------------------
# CORS & CSRF TRUSTED
# ----------------------------
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=["http://localhost:3000", "http://localhost:8000"])
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=["http://localhost:3000", "http://localhost:8000"])

# ----------------------------
# APPLICATIONS
# ----------------------------
INSTALLED_APPS = [
    # Django par défaut
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'drf_yasg',
    'corsheaders',
    'django_extensions',

    # Apps BornSafe
    'accounts.apps.AccountsConfig',
    'actes.apps.ActesConfig',
    'provinces.apps.ProvincesConfig',
]

# ----------------------------
# MIDDLEWARE (ORDRE CORRECT)
# ----------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # DOIT ÊTRE AVANT AuthenticationMiddleware
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # DOIT ÊTRE APRÈS SessionMiddleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'bornsafe_backend.middleware.RequestLoggingMiddleware',
]

# ----------------------------
# URLS & TEMPLATES
# ----------------------------
ROOT_URLCONF = 'bornsafe_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'bornsafe_backend.context_processors.site_info',
            ],
        },
    },
]

WSGI_APPLICATION = 'bornsafe_backend.wsgi.application'

# ----------------------------
# STATIC & MEDIA FILES
# ----------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Création automatique des dossiers
os.makedirs(MEDIA_ROOT, exist_ok=True)
os.makedirs(STATIC_ROOT, exist_ok=True)

# ----------------------------
# DATABASE
# ----------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env("DB_NAME"),
        'USER': env("DB_USER"),
        'PASSWORD': env("DB_PASSWORD"),
        'HOST': env("DB_HOST"),
        'PORT': env("DB_PORT"),
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

# Configuration pour les tests
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }

# ----------------------------
# CACHE
# ----------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# ----------------------------
# AUTHENTIFICATION
# ----------------------------
AUTH_USER_MODEL = 'accounts.User'

LOGIN_URL = '/comptes/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ----------------------------
# INTERNATIONALISATION
# ----------------------------
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Kinshasa'
USE_I18N = True
USE_TZ = True

# ----------------------------
# DRF SETTINGS
# ----------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
        'rest_framework.filters.SearchFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    },
    'EXCEPTION_HANDLER': 'bornsafe_backend.exceptions.custom_exception_handler',
    'DATETIME_FORMAT': '%d/%m/%Y %H:%M:%S',
}

# ----------------------------
# JWT SETTINGS
# ----------------------------
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=env.int("ACCESS_TOKEN_LIFETIME_MINUTES", default=15)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=env.int("REFRESH_TOKEN_LIFETIME_DAYS", default=7)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'JTI_CLAIM': 'jti',
}

# ----------------------------
# SWAGGER SETTINGS
# ----------------------------
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': "Entrez: Bearer <votre_token_jwt>"
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'SUPPORTED_SUBMIT_METHODS': [
        'get', 'post', 'put', 'delete', 'patch'
    ],
}

# ----------------------------
# LOGGING
# ----------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'bornsafe.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'bornsafe': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Créer le dossier logs
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# ----------------------------
# MESSAGE TAGS (pour Tailwind)
# ----------------------------
MESSAGE_TAGS = {
    messages.DEBUG: 'bg-gray-100 text-gray-800',
    messages.INFO: 'bg-blue-100 text-blue-800',
    messages.SUCCESS: 'bg-green-100 text-green-800',
    messages.WARNING: 'bg-yellow-100 text-yellow-800',
    messages.ERROR: 'bg-red-100 text-red-800',
}

# ----------------------------
# DEFAULT PK
# ----------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Ajoutez ceci TOUT À LA FIN de votre fichier settings.py pour forcer le test
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_DOMAIN = None
SESSION_COOKIE_SAMESITE = 'Lax'