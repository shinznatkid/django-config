INSTALLED_APPS += ['rest_framework']

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': '{DJANGO_PROJECT}.rest_exception_handler.exception_handler',
    'DATETIME_FORMAT': "%Y-%m-%d %H:%M:%S",

    # Draft for permission
    # 'DEFAULT_PERMISSION_CLASSES': [
    #     'rest_framework.permissions.IsAuthenticated',
    # ],

    # Draft for authen
    # 'DEFAULT_AUTHENTICATION_CLASSES': [
    #     'rest_framework.authentication.SessionAuthentication',
    # ],

    # Draft for throttle
    # 'DEFAULT_THROTTLE_CLASSES': [
    #     'rest_framework.throttling.ScopedRateThrottle',
    # ],
    # 'DEFAULT_THROTTLE_RATES': {
    #     'resend_otp': '10/second',
    #     'request_otp': '10/second',
    # },
}
