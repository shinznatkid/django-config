
RAVEN_DSN = getattr(configs, 'RAVEN_DSN', False)
if RAVEN_DSN:
    import sentry_sdk

    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        RAVEN_DSN,
        integrations=[DjangoIntegration()],
        send_default_pii=True,
    )

    LOGGING['formatters']['verbose']  = {
        'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
    }
    LOGGING['handlers']['console']['formatter'] = 'verbose'
