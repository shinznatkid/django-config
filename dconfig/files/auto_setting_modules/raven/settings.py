
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

    MIDDLEWARE.append('raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware')
