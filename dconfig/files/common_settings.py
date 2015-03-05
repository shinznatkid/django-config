from utils.misc import import_app
from pathlib import Path
import json


BASE = Path(__file__).resolve().parent.parent
try:
    with (BASE / 'secrets.json').open() as handle:
        SECRETS = json.loads(handle.read())
except IOError:
    SECRETS = {}

SECRET_KEY = SECRETS.get('secret_key', '{SECRET_KEY}')
PRODUCTION = SECRETS.get('production', False)

DEBUG = not PRODUCTION
TEMPLATE_DEBUG = not PRODUCTION

ALLOWED_HOSTS = [SECRETS.get('allowed_hosts')]

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

if not SECRETS.get('engine') or SECRETS.get('engine') == 'sqlite3':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': SECRETS.get('db_name', str(BASE / 'db.sqlite3')),
        }
    }
elif SECRETS.get('engine') == 'mysql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': SECRETS.get('db_name', 'dbname'),
            'USER': SECRETS.get('db_user', 'root'),
            'PASSWORD': SECRETS.get('db_password', 'password'),
            'HOST': SECRETS.get('db_host', '127.0.0.1'),
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
