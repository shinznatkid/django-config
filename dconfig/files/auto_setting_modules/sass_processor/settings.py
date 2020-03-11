
INSTALLED_APPS += ['sass_processor']

STATICFILES_FINDERS += [
    'sass_processor.finders.CssFinder',
]

SASS_PRECISION = 8
