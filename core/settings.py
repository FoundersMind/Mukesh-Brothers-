import os,sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-we4am0xy3$9+%vtmm@jxe!t9s1khr7o8d7u+#x4wxkvwa-o6xj'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'home.apps.HomeConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social_django',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'social_core.backends.google.GoogleOAuth2',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Add LocaleMiddleware after SessionMiddleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'home.middleware.middleware.SwitchSessionCookieMiddleware',  # Add this middleware
    'home.middleware.middleware.CustomAuthenticationMiddleware',  # Add your custom authentication middleware
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'home.context_processor.recent_searches',  # Add your custom context processor if needed
               
                'django.template.context_processors.i18n',  # Add internationalization context processor
            ],
            'builtins': ['django.templatetags.i18n'],  # Enable internationalization template tags
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'Mukesh',
        'USER': 'root',
        'PASSWORD': 'Nj9685070940',
        'HOST': '127.0.0.1',
        'PORT': '3306'
    }
}

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

LANGUAGE_CODE = 'en-us'
LANGUAGES = [
    ('en', 'English'),
    ('hi', 'Hindi'),
    # Add more languages as needed
]

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Add LOCALE_PATHS
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# Media files (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication URLs

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'Home'
LOGOUT_URL = 'logout'
LOGOUT_REDIRECT_URL = 'login'

# Social Auth (Google OAuth2) settings
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '445917318375-8mek6s393lqf1r5el2fqfs3im43j468a.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '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'

# Email backend settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Twilio settings
TWILIO_ACCOUNT_SID = "AC45daf80c65ebd12a7a1d91340f5d8aa4"
TWILIO_AUTH_TOKEN = "31242dad01385092852b0fe22cdd145c"
TWILIO_VERIFY_SID = "VA3223ffa6144df33a06901a5a749a1335"
TWILIO_FROM_NUMBER = "+918770500434"

# Session cookie names
MAIN_SITE_SESSION_COOKIE_NAME = 'main_site_sessionid'
ADMIN_SITE_SESSION_COOKIE_NAME = 'admin_site_sessionid'
SESSION_COOKIE_NAME = MAIN_SITE_SESSION_COOKIE_NAME
