from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler
import traceback
import logging

logger = logging.getLogger('api')


class OperationError(Exception):
    def __init__(self, errcode, msg, data=None):
        self.errcode = errcode
        self.msg = msg
        self.data = data


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if isinstance(exc, ValidationError):
        return Response(status=200, data={"errcode": 400, "msg": "输入的参数有误", "data": {"exc": exc.get_full_details()}})
    elif isinstance(exc, OperationError):
        print(traceback.print_exc())
        return Response(status=200, data={"errcode": exc.errcode, "msg": exc.msg, "data": {"exc": str(exc.data)}})
    if response is not None:
        return response
    else:
        logger.error("Exception: %s" % (traceback.format_exc(-3), ))
        return Response(status=200, data={"errcode": 500, "msg": "服务器异常", "data": {"exc": str(exc)}})
