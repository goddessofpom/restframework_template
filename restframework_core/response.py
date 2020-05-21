import datetime


def jwt_response_payload_handler(token, user=None, request=None):
    user.last_login = str(datetime.datetime.today())
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']
    user.ip = ip
    user.save()

    return {
        'token': token,
        'user_id': user.id,
        'user_permissions': [],
        'name': user.name,
        'gender': user.gender,
    }
