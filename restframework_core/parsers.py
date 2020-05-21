from rest_framework.parsers import BaseParser
from django.http import QueryDict
from django.conf import settings


class CustomerFormParser(BaseParser):
    """
    Parser for form data.
    """
    media_type = 'application/x-www-form-urlencoded'

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Parses the incoming bytestream as a URL encoded form,
        and returns the resulting QueryDict.
        """
        parser_context = parser_context or {}
        encoding = parser_context.get('encoding', settings.DEFAULT_CHARSET)
        return QueryDict(stream.read(), encoding=encoding).dict()