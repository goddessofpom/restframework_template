from rest_framework.permissions import BasePermission
from rest_framework_jwt.settings import api_settings
import jwt
from rest_framework_jwt.authentication import get_authorization_header, BaseJSONWebTokenAuthentication
import traceback
from functools import wraps
from django.http import HttpResponse
from app.models import User


def generate_user_token(user):
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)
    return token


class CustomPermission(BasePermission):
    def has_permission(self, request, view):

        if request.method == "GET":
            return True
        
        if request.user.is_authenticated:
            return True
        return False


class CustomAuthentication(BaseJSONWebTokenAuthentication):

    def authenticate(self, request):
        try:
            auth = get_authorization_header(request)
        except TypeError:
            return None, None

        jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
        if not auth:
            return None, None
        try:
            payload = jwt_decode_handler(auth)
        # 出现jwt解析异常，直接抛出异常，代表非法用户，也可以返回None，作为游客处理
        except jwt.ExpiredSignature:
            return None, None
        except:
            return None, None

        user = self.authenticate_credentials(payload)
        print(user)

        return (user, auth)

def check_login(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
        auth = get_authorization_header(request)
        jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
        if not auth:
            return HttpResponse(status=403)
        try:
            payload = jwt_decode_handler(auth)
        # 出现jwt解析异常，直接抛出异常，代表非法用户，也可以返回None，作为游客处理
        except jwt.ExpiredSignature:
            return HttpResponse(status=403)
        except:
            return HttpResponse(status=403)
        user_id = payload.get("user_id")
        user = User.objects.get(pk=user_id)
        request.user = user
        return func(request, *args, **kwargs)
    
    return inner
