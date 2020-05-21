from qcloudsms_py import SmsMultiSender, SmsSingleSender
from qcloudsms_py.httpclient import HTTPError
from restframework_core.exceptions import OperationError
from django_redis import get_redis_connection
from information.models import SMSMessage


class SMSSender:

    APP_ID = 0
    APP_KEY = ""
    sms_sign = ""

    register_template_id = 0 # 注册
    login_template_id = 0 # 登录
    change_pwd_template_id = 0 # 修改密码

    template = {
        "register": register_template_id,
        "login": login_template_id,
        "change_password": change_pwd_template_id,
    }

    def send_code(self, phone, code, sms_type):
        """
        发送验证码
        """
        # 暂不处理sms_type错误
        create_data = {
            "desc": str(code),
            "template_id": self.template[sms_type],
            "phone": str(phone),
            "fail_reason": "",
            "status": 1,
        }

        if sms_type == "login":
            params = [code, 5] # 目前验证码短信只有 login 有两个参数，在这做处理
        else:
            params = [code]

        try:
            msender = SmsSingleSender(self.APP_ID, self.APP_KEY)
            res = msender.send_with_param(
                     86, phone, self.template[sms_type], params, sign=self.sms_sign, extend="", ext="")

            result = res.get("result")
            if result == 0:
                # 将短信存到redis
                conn = get_redis_connection('default')
                conn.setex("%s_%s" % (phone, sms_type), 300, code)
            else:
                create_data["fail_reason"] = res.get("errmsg")
                create_data["status"] = 0
                # raise OperationError(400, "发送失败, 请稍后再试")

        except HTTPError:
            # raise OperationError(400, "发送失败, 请稍后再试")
            create_data["fail_reason"] = "http错误"
            create_data["status"] = 0

        except Exception as e:
            create_data["fail_reason"] = e
            create_data["status"] = 0
            # raise OperationError(400, "发送失败, 请稍后再试")

        SMSMessage.objects.create(**create_data)

    def send_msg(self, phone, params, msg_type):
        """
        发送普通短信
        params为["xx",]，如果只有一个参数也可以str or int
        """

        desc = ""
        if not isinstance(params, list):
            desc = str(params)
            params = [params]
        else:
            desc = "，".join([str(i) for i in params])

        # "，".join(params), # str 也可 但是list里面不能有int

        # 暂不处理msg_type错误
        create_data = {
            "desc": desc,
            "template_id": self.template[msg_type],
            "phone": str(phone),
            "fail_reason": "",
            "status": 1,
        }

        try:
            msender = SmsSingleSender(self.APP_ID, self.APP_KEY)
            res = msender.send_with_param(
                     86, phone, self.template[msg_type], params, sign=self.sms_sign, extend="", ext="")

            result = res.get("result")
            if result != 0:
                # raise OperationError(400, "发送失败, 请稍后再试")
                create_data["fail_reason"] = res.get("errmsg")
                create_data["status"] = 0

        except HTTPError:
            # raise OperationError(400, "发送失败, 请稍后再试")
            create_data["fail_reason"] = res.get("errmsg")
            create_data["status"] = 0

        except Exception as e:
            # raise OperationError(400, "发送失败, 请稍后再试")
            create_data["fail_reason"] = e
            create_data["status"] = 0
        
        SMSMessage.objects.create(**create_data)


def verify_sms_code(phone, code, sms_type):
    """校验验证码"""
    conn = get_redis_connection('default')
    exist_code = conn.get("%s_%s" % (phone, sms_type))

    if exist_code == None:
        raise OperationError(400, "请发送验证码")

    exist_code = str(exist_code, encoding="utf-8")

    if exist_code != code:
        raise OperationError(400, "验证码错误")