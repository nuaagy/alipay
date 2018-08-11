import uuid

from alipay import AliPay
from django.shortcuts import render, redirect, HttpResponse

from pay import models

ALIPAY_APPID = "2016091700528854"
# 支付宝公钥
# 应用私钥
ALIPAY_URL = 'https://openapi.alipaydev.com/gateway.do'


def goods(request):
    all_goods = models.Goods.objects.all()
    return render(request, 'goods.html', {'goods': all_goods})


def buy(request, gid):
    """购买并支付"""

    g = models.Goods.objects.get(pk=gid)

    # 生成订单
    order_id = str(uuid.uuid4())
    models.Order.objects.create(goods=g, no=order_id)

    # 根据
    #   APPID 2016091700528854
    #   支付宝网关
    #   支付宝公钥 应用私钥
    #  生成跳转url

    # 初始化
    import os
    from django.conf import settings

    alipay = AliPay(
        appid=ALIPAY_APPID,  # APPID
        app_notify_url=None,  # 默认回调url
        # app_private_key_path=os.path.join(settings.BASE_DIR, 'keys', 'app_private_key.pem'),  # 应用私钥
        app_private_key_path='keys/app_private_key.pem',  # 应用私钥
        # alipay_public_key_path=os.path.join(settings.BASE_DIR, 'keys', 'alipay_public_key.pem'),  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        alipay_public_key_path='keys/alipay_public_key.pem',  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        sign_type="RSA2",
        debug=True
    )

    # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=order_id,  # 订单号
        total_amount=str(g.price),  # str
        subject=g.name,  # 商品名称
        return_url='http://132.232.32.54:8000/goods/',  # 重定向
        notify_url=None  # 可选, 不填则使用默认notify url
    )

    # 跳转支付宝支付页面
    alipay_pay_url = ALIPAY_URL + '?' + order_string
    return redirect(alipay_pay_url)


def check_order(request):
    """POST请求，支付成功，支付宝通知 修改订单"""
    if request.method == 'POST':
        alipay = AliPay(
            appid=ALIPAY_APPID,  # APPID
            app_notify_url=None,  # 默认回调url
            app_private_key_path='keys/app_private_key.pem',  # 应用私钥
            alipay_public_key_path='keys/alipay_public_key.pem',  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            sign_type="RSA2",  # 签名类型 RSA 或 默认RSA2
            debug=True  # 默认True沙箱环境/测试环境 False正式环境
        )

        from urllib.parse import parse_qs

        body = request.body.decode('utf-8')
        print(body)

        data = parse_qs(body)
        print(data)

        d = {}
        for k, v in data.items():
            d[k] = v
        print(d)
        signature = d.pop('sign')
        success = alipay.verify(data, signature)
        print(signature)

        if success and data['trade_status'] in ("TRADE_SUCCESS", "TRADE_FINISHED" ):

            out_trade_no = data['out_trade_no']
            models.Order.objects.filter(no=out_trade_no).update(status=2)
            return HttpResponse('trade success')
        else:
            return HttpResponse('trade fail')
    else:
        return HttpResponse('只支持POST请求')



def show(request):
    if request.method == 'GET':
        alipay = AliPay(
            appid=ALIPAY_APPID,
            app_notify_url=None,
            # return_url='http://132.232.32.54:8000/show/',
            app_private_key_path='keys/app_private_key.pem',
            alipay_public_key_path='keys/alipay_public_key.pem',
            sign_type="RSA2",
            debug=True
        )

        query_params = request.GET.dict()
        signature = query_params.pop('sign', None)
        status = alipay.verify(query_params, signature)
        print(query_params)
        return HttpResponse('支付成功') if status else HttpResponse('支付失败')

    else:
        return HttpResponse('只支持GET请求')


def order_list(request):
    """查看所有订单状态"""
    orders = models.Order.objects.all()
    return render(request, 'orders.html', {'orders': orders})