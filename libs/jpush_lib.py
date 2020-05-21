import jpush
from django.conf import settings


class JpushTool(object):
    def __init__(self):
        self._jpush = jpush.JPush(settings.JPUSH_APP_KEY, settings.JPUSH_SECRET)

    def all(self, msg):
        """推送全体"""
        push = self._jpush.create_push()
        push.audience = jpush.all_
        push.notification = jpush.notification(alert=msg)
        push.platform = jpush.all_
        response = push.send()
        return response

    def push_by_reg_id(self, msg, reg_id):
        push = self._jpush.create_push()
        push.audience = {'registration_id': [reg_id]}
        push.notification = jpush.notification(alert=msg)
        push.platform = jpush.all_
        response = push.send()
        return response

    def batch_notification_by_reg_id(self, data):
        """
        根据reg_id推送
        data_format: [
            {'platform: 'all', 'target': 'reg_id', 'notification: {'alert': 'message'}},
            {'platform: 'ios,android', 'target': 'reg_id', 'notification: {'alert': 'message'}},
        ]
        """
        if len(data) > 1000:
            raise ValueError("批量推送不能大于1000条")

        push = self._jpush.create_push()
        response = push.batch_push_by_regid(data)
        print(response)
        return response

    def notification_by_platform(self, android_msg, ios_msg, default_msg):
        """不同平台推送不同消息"""
        push = self._jpush.create_push()
        push.audience = jpush.all_
        ios_notification = jpush.ios(alert=ios_msg)
        android_notification = jpush.android(alert=android_msg)
        push.notification = jpush.notification(alert=default_msg, android=android_notification, ios=ios_notification)
        push.platform = jpush.all_
        response = push.send()
        return response

    def notification_by_tag_or_alias(self, msg, tags, alias=None):
        """根据别名或tag推送消息"""
        push = self._jpush.create_push()

        if alias:
            push.audience = jpush.audience(
                jpush.tag(*tags),
                jpush.alias(*alias),
            )
        else:
            push.audience = jpush.audience(jpush.tag(*tags))

        push.notification = jpush.notification(alert=msg)
        push.platform = jpush.all_
        response = push.send()
        return response
