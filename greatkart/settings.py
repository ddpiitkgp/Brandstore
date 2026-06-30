from pathlib import Path
from decouple import config
import os

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent

# Core settings
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = ['*']  # Use '*' for local testing

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'category',
    'accounts',
    'store',
    'carts',
    'orders',
    'payment',
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CSRF_TRUSTED_ORIGINS = [
    "https://brandstore.iitkgp.ac.in",
    "https://api.razorpay.com",
    #"http://127.0.0.1:8000",
    #"http://127.0.0.1:8080",
    #"http://localhost:8000",
    #"http://localhost:8080",
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_session_timeout.middleware.SessionTimeoutMiddleware',
]

# Session timeout settings
SESSION_EXPIRE_SECONDS = 3600
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True
SESSION_TIMEOUT_REDIRECT = 'accounts/login'

# Application paths
ROOT_URLCONF = 'greatkart.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'category.context_processors.menu_links',
                'carts.context_processors.counter',
            ],
        },
    },
]
WSGI_APPLICATION = 'greatkart.wsgi.application'

# Custom user model
AUTH_USER_MODEL = 'accounts.Account'

# Use local SQLite for local testing
DATABASES = {
    'default': {
        ## MYSQL        
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'brandingdb'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'rootpassword'),
        'HOST': os.environ.get('DB_HOST', 'mariadb'), # Match the service name
        'PORT': os.environ.get('DB_PORT', '3306'),
        'CONN_MAX_AGE': 60,
        ##  SQLITE
        ## 'ENGINE': 'django.db.backends.sqlite3',
        ## #'NAME': BASE_DIR / 'dbdata/db.sqlite3',
        ## 'NAME': '/dbdata/db.sqlite3', 
        ## # Uncomment above line and comment previous line for production server
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Localization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# CORRECTED Static files configuration for BOTH root-level AND app-level static folders


STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',    
    'django.contrib.staticfiles.finders.AppDirectoriesFinder', 
]


STATIC_URL = 'https://brandstore.iitkgp.ac.in/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/media')

# Messages config
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {messages.ERROR: 'danger'}

# Email config
EMAIL_BACKEND = 'greatkart.email_backend.CertifiEmailBackend'
# Uncomment this in Production server
EMAIL_HOST = config('EMAIL_HOST', default='10.3.103.129')
EMAIL_PORT = config('EMAIL_PORT', default=25, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL =  config('DEFAULT_FROM_EMAIL', default='')
ADMIN_EMAILS = config('ADMIN_EMAILS', default='') 

RAZORPAY_KEY_ID = "rzp_test_SxvnTfLd4RDRpe"
RAZORPAY_KEY_SECRET = "J55IBv1dU6wZeqNy27eDAsel"
RAZORPAY_WEBHOOK_SECRET = "webhook_secret"

