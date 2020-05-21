from rest_framework import pagination
from rest_framework.response import Response
from collections import OrderedDict


class PageSet(pagination.PageNumberPagination):
    page_size = 15
    page_size_query_param = "size"
    page_query_param = "page"
    max_page_size = 50

    def get_paginated_response(self, data):
        errcode = 0
        msg = 'ok'
        if not data:
            msg = "no data"
            data = []

        return Response(OrderedDict([
            ('errcode', errcode),
            ('msg', msg),
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('data', data),
        ]))
