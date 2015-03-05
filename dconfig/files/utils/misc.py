# -*- coding: utf-8 -*-


def import_app(app, installed_apps):
    try:
        __import__(app)
        installed_apps.append(app)
        return True
    except ImportError:
        pass
    return False
