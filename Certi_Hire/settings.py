from decouple import config
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent



SECRET_KEY = 'django-insecure-)mv3=!ir)-sn@y__gjh6aegn-66e@5vhs_&*9^)v20n9=4mflk'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'daphne',
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'assessment',
    'gigs',
    'orders',
    'chat',
    'dashboard',
    'landing',
    'payments',
    'notifications',
    'reviews',
    'profiles',
    'adminpanel',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Certi_Hire.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "notifications.context_processors.notification_context",
                "chat.context_processors.message_context",
            ],
        },
    },
]

WSGI_APPLICATION = 'Certi_Hire.wsgi.application'
ASGI_APPLICATION = "Certi_Hire.asgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'certi',
        'USER': 'postgres',
        'PASSWORD': '1234',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators
CASHFREE_CLIENT_ID = config("CASHFREE_CLIENT_ID")
CASHFREE_CLIENT_SECRET = config("CASHFREE_CLIENT_SECRET")
CASHFREE_BASE_URL = config("CASHFREE_BASE_URL")

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / "static",
]
# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = "accounts.User"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

CHANNEL_LAYERS = {

    "default": {

        "BACKEND": "channels.layers.InMemoryChannelLayer",

    },

}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = "smtp.gmail.com"

EMAIL_PORT = 587

EMAIL_USE_TLS = True

EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='your_email@gmail.com')

EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='your_app_password')
DEFAULT_FROM_EMAIL = (
    config('DEFAULT_FROM_EMAIL', default='CertiHire <noreply@certihire.com>')
)