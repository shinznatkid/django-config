import os


TEST_PROJECT_ROOT = os.path.abspath(
    os.environ.get('TEST_PROJECT_ROOT', '/tmp/'),
)

STATIC_ROOT = os.path.join(TEST_PROJECT_ROOT, 'static_root')

STATIC_URL = '/static/'

BOWER_INSTALLED_APPS = (
    'jquery',
    'bootstrap',
)

SECRET_KEY = 'secret'

INSTALLED_APPS = (
    'dconfig',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}
