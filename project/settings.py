from decouple import config
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

SECRET_KEY = config('SECRET_KEY', default='django-insecure-#kwdnk7_mh*f=xwax4z^k41^js44am1zzx8%wd&fkkn-q0bl+q') # Added default for safety if .env is missing
DEBUG = config('DEBUG', default=True, cast=bool) # Use decouple for DEBUG

ALLOWED_HOSTS = [] # Consider loading from environment variable for production

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app1'
]

AUTH_USER_MODEL = 'app1.Account'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
             'libraries':{ # Added this to load custom template tags easily
                'custom_filters': 'app1.templatetags.custom_filters',
            }
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [STATIC_DIR]
MEDIA_URL = 'media/'
MEDIA_ROOT = MEDIA_ROOT # Corrected variable name

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email Settings (using decouple for sensitive info)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' 

# Keep these settings as they seem correct for Gmail SMTP
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='') # Should load 'pythonbyteme@gmail.com'
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='') # Should load your app password
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)
# Razorpay Settings (using decouple)
# RAZORPAY_KEY_ID = config('RAZORPAY_KEY_ID', default='YOUR_RAZORPAY_KEY_ID')
# RAZORPAY_KEY_SECRET = config('RAZORPAY_KEY_SECRET', default='YOUR_RAZORPAY_KEY_SECRET')

# Session settings (Optional: Helps manage session data for OTP)
SESSION_ENGINE = 'django.contrib.sessions.backends.db' # Or cache if preferred
SESSION_COOKIE_AGE = 1209600  # 2 weeks, in seconds
SESSION_SAVE_EVERY_REQUEST = True # Ensures session is saved
