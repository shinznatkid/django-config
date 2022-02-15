from .common_settings import *  # pylint: disable=W0401 NOSONAR


INSTALLED_APPS += []


try:
    from configs import *  # pylint: disable=W0401 NOSONAR
except ImportError:
    pass
