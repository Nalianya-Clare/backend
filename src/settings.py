import os
from pathlib import Path

import dotenv
import sentry_sdk

from config import config
from config.config import ckeditor_config, jazzmin_config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
dotenv.load_dotenv()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', '')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.environ.get("DEBUG", default=0))

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').split(' ')

# setup sentry for error logging and monitoring (will be sending realtime error emails.)
# sentry_sdk.init(
#     dsn="https://st.de.sentry.io/4507862121250896",
#     # Set traces_sample_rate to 1.0 to capture 100%
#     # of transactions for tracing.
#     traces_sample_rate=1.0,
#     # Set profiles_sample_rate to 1.0 to profile 100%
#     # of sampled transactions.
#     # We recommend adjusting this value in production.
#     profiles_sample_rate=1.0,
# )

# Application definition
INSTALLED_APPS = [
    'daphne',
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # editor settings
    'ckeditor',
    'django_ckeditor_5',
    'ckeditor_uploader',

    'adrf',
    'rest_framework',
    'corsheaders',
    'storages',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django_celery_beat',
    'django_celery_results',

    # Documentation
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'drf_yasg',

    'account.apps.AccountConfig',
    'appointments.apps.AppointmentsConfig',
    'walletApp.apps.WalletappConfig',
    'blogs.apps.BlogsConfig',
]

ENVIRONMENT = os.environ.get("ENVIRONMENT", "dev")

# CELERY CONFIG
redis_url = os.environ.get('REDIS_URL')
CELERY_BROKER_URL = f'{redis_url}/0'
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'django_celery_results.backends.database:DatabaseBackend'
CELERY_CACHE_BACKEND = 'django_redis.cache.RedisCache'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'{redis_url}/0',
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                'max_connections': 100,
                'retry_on_timeout': True,
                # 'ssl_cert_reqs': None
            },
        }
    },
    'celery': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': '{}/1'.format(redis_url),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                'max_connections': 100,
                'retry_on_timeout': True,
                # 'ssl_cert_reqs': None
            },
        }
    }
}

SIMPLE_JWT = config.jwt_auth_config(SECRET_KEY)

AUTH_USER_MODEL = 'account.User'

# Rest_framework config
REST_FRAMEWORK = config.rest_framework_config()

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'JWT Authorization header using the Bearer scheme. Example: "Authorization: Bearer {token}"',
        }
    },
    'USE_SESSION_AUTH': False,  # Disable session auth if you're using JWT exclusively
}

# Swagger and redoc setup
SPECTACULAR_SETTINGS = config.api_docs_config()

# Middlewares
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Custom Middlewares
    # 'middlewares.singlesession.OneSessionPerUser'
]

ROOT_URLCONF = 'src.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI_APPLICATION = 'src.wsgi.application'
ASGI_APPLICATION = 'src.asgi.application'

# Database config
DATABASES = {
    'default': {
        'ENGINE': os.environ.get("SQL_ENGINE", "django.db.backends.sqlite3"),
        'NAME': os.environ.get("DB_NAME"),
        'USER': os.environ.get("DB_USER", "user"),
        'HOST': os.environ.get("DB_HOST", "localhost"),
        'PORT': os.environ.get("DB_PORT", "5432"),
        'PASSWORD': os.environ.get("DB_PASSWORD", "password"),
        'CONN_MAX_AGE': 60,
        # Connection pool settings
        'POOL_OPTIONS': {
            'POOL_SIZE': 20,  # Maximum number of connections in the pool
            'MAX_OVERFLOW': 10,  # Maximum overflow beyond the pool size
            'RECYCLE': 3600,  # Time (in seconds) before recycling a connection
            'POOL_CLASS': 'QueuePool',
        }
    },
    'TEST': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'dev.sqlite3',

    },
}

# For testing database
# if 'test' in sys.argv or 'test_coverage' in sys.argv: # Covers regular testing and django-coverage
#     DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'
#     DATABASES['default']['NAME'] = ':memory:'

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
            'user_attributes': ('username', 'email', 'first_name', 'last_name'),
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',

    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Log configuration
LOGGING = config.logging_config(BASE_DIR)

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

# TIME_ZONE = 'UTC'
TIME_ZONE = 'Africa/Nairobi'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

USE_S3 = os.environ.get('USE_S3')

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'static/media')

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_5_CONFIGS = ckeditor_config()

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Site Security
CORS_ALLOWED_ORIGINS = [
    "https://myhela.africa",
    "http://217.76.59.68:7070",
    "http://localhost:3000",          
    "http://127.0.0.1:3000",             
    "https://myhela.vercel.app",         
    "http://localhost:5173",              
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://217.76.59.68:4174/",
    "http://127.0.0.1:4173",
]
CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_CREDENTIALS = False

SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = False
SESSION_COOKIE_SAMESITE = 'Lax'

CSRF_COOKIE_SECURE = False  # Ensure CSRF cookie is only sent over HTTPS
CSRF_COOKIE_HTTPONLY = False  # Ensure CSRF cookie is accessible only via HTTP(S) requests
CSRF_COOKIE_SAMESITE = 'Lax'

CSRF_TRUSTED_ORIGINS = [
     "https://myhela.africa",
     "http://217.76.59.68:4174"
    "http://217.76.59.68:7070",
    "http://localhost:3000",          
    "http://127.0.0.1:3000",             
    "https://myhela.vercel.app",         
    "http://localhost:5173",              
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
]

# prevent cross-site scripting attacks
CSP_IMG_SRC = ("'self'",)

CSP_STYLE_SRC = ("'self'",)

CSP_SCRIPT_SRC = ("'self'",)

X_FRAME_OPTIONS = 'SAMEORIGIN'

SITE_URL = os.environ.get('SITE_URL', 'http://localhost:8000')
SITE_ID = 1
APPEND_SLASH = False

DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10mb = 10 * 1024 *1024

# Mail setup
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND')
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT'))
EMAIL_USE_TLS = bool(os.environ.get('EMAIL_USE_TLS'))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_REPLY_TO = os.environ.get('EMAIL_REPLY_TO')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')

# Google Setup
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
GOOGLE_PROJECT_ID = os.environ.get('GOOGLE_PROJECT_ID')
BASE_BACKEND_URL = os.environ.get('BASE_BACKEND_URL', 'http://localhost:8000')
FRONT_END_URL = os.environ.get('FRONT_END_URL', 'http://localhost:3000')
CONSOLE_URL = os.environ.get('FRONT_END_CONSOLE_URL', 'http://localhost:3000')

ADMIN_URL = os.environ.get('ADMIN_URL')

# Moodle Setup
JAZZMIN_SETTINGS = jazzmin_config()

# CELERY
CELERYD_MAX_MEMORY_PER_CHILD = 300000
CELERYD_MAX_TASKS_PER_CHILD = 100

PARENT_FOLDER_ID = os.environ.get('PARENT_FOLDER_ID')
PARENT_FOLDER_ID_ID = os.environ.get('PARENT_FOLDER_ID_ID')
GOOGLE_SCOPES = os.environ.get('GOOGLE_SCOPES')

PASSWORD_EXPIRY_DAYS = os.environ.get('PASSWORD_EXPIRY_DAYS', 120)

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY')
PAYSTACK_PUBLIC_KEY = os.environ.get('PAYSTACK_PUBLIC_KEY')