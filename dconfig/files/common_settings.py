from utils.misc import import_app
from pathlib import Path

try:
    import configs
except ImportError:
    configs = {}


BASE = Path(__file__).resolve().parent.parent

SECRET_KEY = getattr(configs, 'SECRET_KEY', '+y01%7#9aipmcca171@(%%3i0v#mi(f32&a-(+r0=w_i7mj2yk')
PRODUCTION = getattr(configs, 'PRODUCTION', False)

DEBUG = not PRODUCTION
TEMPLATE_DEBUG = not PRODUCTION

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

TEMPLATE_DIRS = [str(BASE / 'templates')]
STATIC_URL = '/static/'
STATICFILES_DIRS = [str(BASE / 'static')]
STATIC_ROOT = str(BASE / 'static_root')
MEDIA_URL = '/media/'
MEDIA_ROOT = str(BASE / 'media')

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
]

if DEBUG:
    if import_app('debug_toolbar', INSTALLED_APPS):
        INTERNAL_IPS = ['127.0.0.1']
        MIDDLEWARE_CLASSES.insert(
            MIDDLEWARE_CLASSES.index('django.middleware.common.CommonMiddleware') + 1,
            'debug_toolbar.middleware.DebugToolbarMiddleware')

if import_app('picker', INSTALLED_APPS):
    PICKER_INSTALLED_APPS = (
        'jquery',
        'bootstrap',
        'bootstrap-cosmo',
        'less',
    )

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

RAVEN_DSN = getattr(configs, 'RAVEN_DSN', False)
if RAVEN_DSN:
    import raven
    INSTALLED_APPS += [
        'raven.contrib.django.raven_compat',
    ]

    RAVEN_CONFIG = {
        'dsn': RAVEN_DSN,
        'release': raven.fetch_git_sha(str(BASE)),
    }

    LOGGING['formatters']['verbose']  = {
        'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
    }
    LOGGING['handlers']['sentry'] = {
        'level': 'ERROR',
        'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
    }
    LOGGING['root'] = {
        'level': 'WARNING',
        'handlers': ['sentry'],
    }
    LOGGING['loggers']['raven'] = {
        'level': 'DEBUG',
        'handlers': ['console'],
        'propagate': False,
    }
    LOGGING['loggers']['sentry.errors'] = {
        'level': 'ERROR',
        'handlers': ['console'],
        'propagate': False,
    }
    LOGGING['handlers']['console']['formatter'] = 'verbose'

    MIDDLEWARE_CLASSES.append('raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware')
