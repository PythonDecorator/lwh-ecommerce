"""
Django settings for Gimsap project.

Generated by 'django-admin startproject' using Django 4.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import datetime
from pathlib import Path
import os
from decouple import config


BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG')
if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # One year in seconds
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

ALLOWED_HOSTS = ["*"]

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django.contrib.sites',

    #  third party
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'crispy_forms',
    'django_celery_beat',
    'post_office',
    'crispy_bootstrap4',


    # my apps
    'orders',
    'items',
    'users',
    'home',
    'dashboard',
]

CRISPY_TEMPLATE_PACK = 'bootstrap4' 

MIDDLEWARE = [
    # Todo : for heroku will be removed later
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Gimsap.urls'

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
                'items.context_processors.add_variable_to_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'Gimsap.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
#  Add configuration for static files storage using whitenoise
# Todo: note i installed  gunicorn dj-database-url whitenoise psycopg2 for heroku

if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'staticfiles')
]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# django allauth
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
LOGIN_REDIRECT_URL = '/'
SOCIALACCOUNT_QUERY_EMAIL = True

SIGNUP_REDIRECT_URL = LOGIN_REDIRECT_URL
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True
ACCOUNT_SIGNUP_REDIRECT_URL = LOGIN_REDIRECT_URL
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_SUBJECT_PREFIX = ''
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300

AUTHENTICATION_BACKENDS = (
    # Needed to log in by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by e-mail
    # "allauth.account.auth_backends.AuthenticationBackend"
)

EMAIL_BACKEND = "post_office.EmailBackend"
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_PORT = config('EMAIL_PORT')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = config('EMAIL_HOST_USER')

POST_OFFICE = {
    'DEFAULT_PRIORITY': 'now',
    'MESSAGE_ID_ENABLED': True,
    'MAX_RETRIES': 5,
    'RETRY_INTERVAL': datetime.timedelta(minutes=15),  # Schedule to be retried 15 minutes later
    'THREADS_PER_PROCESS': 10,
}

ADMINS = [('Afenikhena Favour', config('ADMIN_MAIL'),)]

SITE_ID = 1

CRISPY_TEMPLATE_PACK = 'bootstrap4'

DOMAIN_URL = config('DOMAIN_URL', default="https://gimsap.com")

# change the credentials if on debug
if DEBUG:
    PAYPAL_CLIENT_ID = config('DEBUG_PAYPAL_CLIENT_ID')
    PAYPAL_SECRET_KEY = config('DEBUG_PAYPAL_SECRET_KEY')
    PAYPAL_URL = config('DEBUG_PAYPAL_URL')
else:
    PAYPAL_CLIENT_ID = config('PAYPAL_CLIENT_ID')
    PAYPAL_SECRET_KEY = config('PAYPAL_SECRET_KEY')
    PAYPAL_URL = config('PAYPAL_URL')

GOOGLE_API_KEY = config('GOOGLE_API_KEY')
