from rest_framework.response import Response
from rest_framework import viewsets
from libs.tools import json_success
from rest_framework.parsers import JSONParser, MultiPartParser
from .parsers import CustomerFormParser


class CustomModelViewSet(viewsets.ModelViewSet):
    parser_classes = [JSONParser, CustomerFormParser, MultiPartParser]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({"errcode": 0, "msg": "ok", "data": {}}, status=200)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return Response({"errcode": 0, "msg": "ok", "data": {**response.data}})

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        return Response({"errcode": 0, "msg": "ok", "data": {}}, status=200)

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        return Response({"errcode": 0, "msg": "ok", "data": {}}, status=200)

    def list(self, request, *args, **kwargs):
        no_page = request.query_params.get('noPage', None)
        paginatable = not no_page or (no_page != "1" and no_page != "true")
        if paginatable:
            return super().list(request, *args, **kwargs)
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(queryset, many=True)
        return json_success(serializer.data)
