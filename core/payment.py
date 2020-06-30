import os
from xml.dom.minidom import parseString
from django.conf import settings
from wechatpy import WeChatPay
from alipay import AliPay
from .utils import gen_order_code
from django.http import HttpResponse
from restframework_core.exceptions import OperationError


class BasePayment(object):
    
    def pay_success(self, out_trade_no):
        pass

    def pay_fail(self):
        raise OperationError(400, "支付失败")

    def _gen_out_trade_no(self):
        return gen_order_code()

class AliPayment(BasePayment):
    def __init__(self, alipay):
        self.alipay = alipay

    def launch_order(self, subject_name, total_amount, open_id=None):
        out_trade_no = self._gen_out_trade_no()
        order_string = self.alipay.api_alipay_trade_app_pay(
            subject=subject_name, out_trade_no=out_trade_no, total_amount=total_amount
        )
        return order_string, out_trade_no

    def _parse_response(self, response_data):
        sign = response_data.pop("sign", None)
        status = self.alipay.verify(response_data, sign)
        if status:
            return response_data.pop("out_trade_no")
        self.pay_fail()

    def ali_pay_success_callback(self, response_data):
        out_trade_np = self._parse_response(response_data)
        self.pay_success(out_trade_no)
        return HttpResponse("success")


class WxPayment(BasePayment):
    def __init__(self, wxpay, trade_type="APP"):
        self.wxpay = wxpay
        self.trade_type = trade_type

    def launch_order(self, subject_name, total_amount, open_id):
        out_trade_no = self._gen_out_trade_no()
        order = self.wxpay.order.create(
            trade_type = self.trade_type,
            body = subject_name,
            total_fee = total_amount,
            notify_url = settings.WX_PAY_APP_NOTIFY_URL,
            user_id = openid,
            out_trade_no=out_trade_no
        )

        if trade_type == "APP":
            order_string = wxpay.order.get_appapi_params(order["prepay_id"])
        else:
            order_string = wxpay.jsapi.get_jsapi_params(order["prepay_id"], jssdk=True)
        return order_string, out_trade_no

    def _parse_xml(self, response_xml):
        e_tree = parseString(response_xml)
        root_node = e_tree.documentElement
        return_code = root_node.getElementsByTagName("return_code")[0].firstChild.data
        if return_code == "FAIL":
            self.pay_fail()
        out_trade_no = root_node.getElementsByTagName("out_trade_no")[0].firstChild.data
        return out_trade_no

    def wx_pay_success_callback(self, response_xml):
        out_trade_no = self._parse_xml(response_xml)
        self.pay_success(out_trade_no)
        response = "<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>"
        return HttpResponse(response)



class WalletPayment(BasePayment):
    pass


class PaymentFactory(object):
    
    def get_payment(self, ctype, trade_type="APP"):
        if ctype == 1:
            return self._init_ali_pay()
        elif ctype == 2:
            return self._init_wx_pay(trade_type)
        else:
            return self._init_wallet_pay()

    def _init_ali_pay(self):
        path = os.path.abspath(os.path.dirname(__file__))
        private_file = open(settings.ALI_PAY_PRIVATE_KEY_PATH, "r")
        private_key = private_file.read()
        private_file.close()

        public_file = open(settings.ALI_PAY_PUBLIC_KEY_PATH, "r")
        public_key = public_file.read()
        public_file.close()

        debug = settings.DJANGO_IN_DOCKER_DEBUG is None
        appid = settings.ALI_PAY_APP_ID
        app_notify_url = settings.ALI_PAY_APP_NOTIFY_URL

        alipay = AliPay(
          appid=appid, app_notify_url=app_notify_url, app_private_key_string=private_key, alipay_public_key_string=public_key, debug=debug
        )
        return AliPayment(alipay)

    def _init_wx_pay(self, trade_type="APP"):
        if trade_type == "JSAPI":
            wxpay = WeChatPay(
                appid=settings.WEIXIN_PUBLIC["app_id"], api_key=settings.WX_PAY_API_KEY, mch_id=settings.WX_PAY_MCH_ID, mch_cert=settings.WX_PAY_MCH_CERT_PATH,
                mch_key=settings.WX_PAY_MCH_KEY_PATH
            )
        else:
            wxpay = WeChatPay(
                appid=settings.WX_PAY_APP_ID, api_key=settings.WX_PAY_API_KEY, mch_id=settings.WX_PAY_MCH_ID, mch_cert=settings.WX_PAY_MCH_CERT_PATH,
                mch_key=settings.WX_PAY_MCH_KEY_PATH
            )
        return WxPayment(wxpay, trade_type)

    def _init_wallet_pay(self):
        return WalletPayment()
