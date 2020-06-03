from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
# from pywe_django.settings import w

# 客户系统、商户系统、订单系统、优惠券、余额、购物车、物流模板、会员卡（积分）
# 修改的商品保存历史版本及改动
# 调用支付接口保存传入参数和回调参数
# 单商户系统自动创建商户

# @w.login_required
def index(request):
    from backbone.models import Client
    import time

    Client.objects.create(uid=(time.time()))

    a = Client.objects.all().first()
    a.cart
    a.cart
    a.cart

    return HttpResponse('hellow word')


@csrf_exempt
def upload_image(request):
    """
    @api {post} /upload_image 上传图片
    @apiVersion 1.0.0
    @apiGroup common
    @apiName 上传图片

    @apiParam {Object} file

    @apiSuccess {String} url 图片url
    """
    if request.method == 'POST':
        try:
            file = request.FILES["file"]
        except Exception:
            return json_failed(400, "请选择上传图片")

        image_path, name = save_image(file)
        url = os.path.join(settings.BASE_URL, "media", image_path, name)
        return json_success({"url": url})
    return HttpResponseNotAllowed("POST")
