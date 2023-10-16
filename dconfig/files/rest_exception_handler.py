import json
import logging
import traceback
from collections import OrderedDict

from rest_framework import exceptions, status
from rest_framework.views import set_rollback, exception_handler as base_exception_handler
from rest_framework.response import Response

from django.http import Http404
from django.conf import settings
from django.core.exceptions import PermissionDenied


def handle_validation_error(exc):
    '''
    exc.detail can be 2 types
    1. dict e.g. {'name': ['This field is required.']}
    2. list e.g. ['field name is required.']
    '''
    headers = {}

    if isinstance(exc.detail, dict):
        error_dict = exc.detail
        error_messages = []
        for key, val in error_dict.items():
            if isinstance(val, list):
                for error_val in val:
                    error_messages.append(f'[{key}] {error_val}')
    elif isinstance(exc.detail, list):
        error_messages = exc.detail

    if error_messages:
        error_message = '\n'.join(error_messages)
    else:
        error_message = 'bad request'

    data = _get_status_dict(code='BAD_REQUEST', message=error_message)

    set_rollback()
    return Response(data, status=status.HTTP_400_BAD_REQUEST, headers=headers)


def handle_api_exception(exc):
    logger = logging.getLogger('error')
    headers = {}
    if getattr(exc, 'auth_header', None):
        headers['WWW-Authenticate'] = exc.auth_header
    if getattr(exc, 'wait', None):
        headers['Retry-After'] = str(exc.wait)

    if isinstance(exc.detail, (list, dict)):
        data = exc.detail
    else:
        default_code = getattr(exc, 'default_code', 'INTERNAL_SERVER_ERROR')
        code = getattr(exc, 'code', default_code.upper())
        data = _get_status_dict(code=code, message=exc.detail)

    trace = getattr(exc, 'trace', {})
    data['trace'] = trace

    set_rollback()

    try:
        logger.info(json.dumps(data))
    except Exception:  # เผื่อมีเคสที่ serialize ข้อมูลไม่ได้ เช่นวันที่
        pass

    return Response(data, status=exc.status_code, headers=headers)


def handle_404():
    msg = 'Not found.'
    data = _get_status_dict(code='NOT_FOUND', message=msg)
    set_rollback()
    return Response(data, status=status.HTTP_404_NOT_FOUND)


def handle_permission_denied():
    msg = 'Permission denied.'
    data = _get_status_dict(code='FORBIDDEN', message=msg)
    set_rollback()
    return Response(data, status=status.HTTP_403_FORBIDDEN)


def handle_unseen_error(exc):
    msg = 'Internal server error.'
    code = getattr(exc, 'code', 'INTERNAL_SERVER_ERROR')
    data = _get_status_dict(code=code, message=msg)
    set_rollback()

    traceback.print_exc()
    if settings.RAVEN_DSN:
        try:
            from sentry_sdk import capture_exception
            capture_exception(exc)
        except Exception:
            pass

    return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def exception_handler(exc, context):
    """
    Returns the response that should be used for any given exception.

    By default we handle the REST framework `APIException`, and also
    Django's built-in `Http404` and `PermissionDenied` exceptions.

    Any unhandled exceptions may return `None`, which will cause a 500 error
    to be raised.
    """
    if isinstance(exc, exceptions.ValidationError):  # this is ValidationError
        return handle_validation_error(exc)

    if isinstance(exc, exceptions.APIException):
        return handle_api_exception(exc)

    if isinstance(exc, Http404):
        return handle_404()

    if isinstance(exc, (PermissionDenied, exceptions.NotAuthenticated, exceptions.AuthenticationFailed)):
        return handle_permission_denied()

    if isinstance(exc, Exception):
        return handle_unseen_error(exc)

    return base_exception_handler(exc, context)


def _get_status_dict(code: str, message: str):
    '''
    return { "status" {"code": "FAILED", "message": "Failed"}}
    '''
    data = {
        'status': OrderedDict(code=code, message=message)
    }
    return data
