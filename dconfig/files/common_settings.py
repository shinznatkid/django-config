from utils.misc import import_app
from pathlib import Path


class EnvironDict(object):

    def __init__(self, prefix):
        self.prefix = prefix

    def __getattr__(self, attrname):
        import os
        if attrname in os.environ:
            return os.environ[self.prefix + attrname]
        raise AttributeError()

try:
    import configs
except ImportError:
    try:
        configs = EnvironDict('DJANGO_')
    except:
        configs = {}


PROJECT_PATH = Path(__file__).resolve().parent
BASE = PROJECT_PATH.parent

SECRET_KEY = getattr(configs, 'SECRET_KEY', '+y01%7#9aipmcca171@(%%3i0v#mi(f32&a-(+r0=w_i7mj2yk')
PRODUCTION = getattr(configs, 'PRODUCTION', False)

DEBUG = not PRODUCTION

ALLOWED_HOSTS = getattr(configs, 'ALLOWED_HOSTS', [])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
]

ROOT_URLCONF = '{DJANGO_PROJECT}.urls'
WSGI_APPLICATION = '{DJANGO_PROJECT}.wsgi.application'

ENGINE = getattr(configs, 'ENGINE', None)
if not ENGINE or ENGINE == 'sqlite3':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': getattr(configs, 'DB_NAME', str(BASE / 'db.sqlite3')),
        }
    }
elif ENGINE == 'mysql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': getattr(configs, 'DB_NAME', 'dbname'),
            'USER': getattr(configs, 'DB_USER', 'root'),
            'PASSWORD': getattr(configs, 'DB_PASSWORD', 'password'),
            'HOST': getattr(configs, 'DB_HOST', '127.0.0.1'),
        }
    }

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Bangkok'
USE_I18N = True
USE_L10N = True
USE_TZ = False
DATE_FORMAT = "SHORT_DATE_FORMAT"

STATIC_URL = '/static/'
STATICFILES_DIRS = [str(BASE / 'static')]
STATIC_ROOT = str(BASE / 'static_root')
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]
MEDIA_URL = '/media/'
MEDIA_ROOT = str(BASE / 'media')

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

'''
How to access or edit this templates

use:
    TEMPLATES['keys'] = 'value'
example:
    TEMPLATES['OPTIONS']['context_processors'].append('mycontext_processors')

'''
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(BASE / 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': getattr(configs, 'TEMPLATE_DEBUG', DEBUG),
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

if DEBUG:
    if import_app('debug_toolbar', INSTALLED_APPS):
        INTERNAL_IPS = ['127.0.0.1']
        MIDDLEWARE.insert(
            MIDDLEWARE.index('django.middleware.common.CommonMiddleware') + 1,
            'debug_toolbar.middleware.DebugToolbarMiddleware')

    import_app('dconfig', INSTALLED_APPS)  # Try import dconfig it self


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',  # Older version use django.utils.log.NullHandler
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARN',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'WARN',
        },
    },
}


# Automation path
from .auto_settings import *  # pylint: disable=W0401

INSTALLED_APPS += AUTO_INSTALLED_APPS

for package in AUTO_INSTALLED_APPS:
    setting_path = PROJECT_PATH / 'auto_setting_modules' / package / 'settings.py'
    with open(str(setting_path), 'rt') as f:
        raw_script = f.read()
    exec(raw_script)
