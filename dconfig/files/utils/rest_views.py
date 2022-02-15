'''
Use for Customize Base RestFramework Views for this structure

{
    "status": {
        "code": status_code,
        "message": status_message
    },
    "data": data
}
'''
from collections import OrderedDict

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView as BaseAPIView
from rest_framework.generics import CreateAPIView as BaseCreateAPIView
from rest_framework.generics import UpdateAPIView as BaseUpdateAPIView
from rest_framework.generics import RetrieveAPIView as BaseRetrieveAPIView
from rest_framework.generics import ListAPIView as BaseListAPIView
from rest_framework.generics import ListCreateAPIView as BaseListCreateAPIView
from rest_framework.generics import RetrieveUpdateAPIView as BaseRetrieveUpdateAPIView
from rest_framework.generics import GenericAPIView as BaseGenericAPIView


def encapsulation_result(data, status_code, status_message):
    context = {
        'status': {
            'code': status_code,
            'message': status_message
        },
        'data': data
    }
    return context


class APIView(BaseAPIView):

    def encap_success_overhead(self, data):
        ret = OrderedDict()
        ret['status'] = {
            "code": "SUCCESS",
            "message": "Success."
        }
        ret['data'] = data
        return ret


class GenericAPIView(BaseGenericAPIView):

    def encap_success_overhead(self, data):
        ret = OrderedDict()
        ret['status'] = {
            "code": "SUCCESS",
            "message": "Success."
        }
        ret['data'] = data
        return ret

    def get_success_headers(self, data):
        headers = super().get_success_headers(data)
        return headers


class CreateAPIView(BaseCreateAPIView):

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        context = encapsulation_result(serializer.data, 'SUCCESS', 'Success')
        return Response(context, status=status.HTTP_201_CREATED, headers=headers)


class UpdateAPIView(BaseUpdateAPIView):

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        context = encapsulation_result(serializer.data, 'SUCCESS', 'Success')
        return Response(context)


class RetrieveAPIView(BaseRetrieveAPIView):

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        context = encapsulation_result(serializer.data, 'SUCCESS', 'Success')
        return Response(context)


class ListAPIView(BaseListAPIView, GenericAPIView):

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        context = encapsulation_result(serializer.data, 'SUCCESS', 'Success')
        return Response(context)


class ListCreateAPIView(BaseListCreateAPIView):

    list = ListAPIView.__dict__['list']
    create = CreateAPIView.__dict__['create']


class RetrieveUpdateAPIView(BaseRetrieveUpdateAPIView):

    retrieve = RetrieveAPIView.__dict__['retrieve']
    update = UpdateAPIView.__dict__['update']
