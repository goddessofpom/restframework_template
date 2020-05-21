from __future__ import unicode_literals

from django.utils import timezone
from django.db import models
from libs.tools import Base

# 建议 import backbone.models as bbm, 使用时 bbm.Client 不会和现有项目冲突


class Client(Base):
    """客户"""

    uid = models.CharField('UID', max_length=200)
    nickname = models.CharField('昵称', max_length=200, blank=True, null=True)
    avatar = models.CharField('头像', max_length=200, blank=True, null=True)
    phone = models.CharField('手机号', max_length=200, blank=True, null=True)
    balance = models.IntegerField('余额', default=0)

    config = {
        'create': ['uid'],
        'search': ['uid', 'nickname', 'phone'],
        'default': ['id', 'uid', 'nickname', 'avatar'],
        'detail': ['phone'],
        'privacy': ['balance', 'created', 'updated'],
    }

    '''
    # 演示如何动态计算属性
    @property
    def privacy(self):
     
        privacy = super().privacy
        privacy['demo'] = 11
        return privacy
    '''

    # 按页码获取账单记录
    def bill_list(self, page):
        return Bill.objects.filter(client=self).page(page)

    # 购物车列表
    @property
    def cart_list(self):
        return Bill.objects.filter(client=self)

    # 购物车添加商品
    def cart_add(self, product):
        cart = Cart.objects.filter(client=self, product=product).first()
        if cart:
            cart.number += 1
            cart.save()
        else:
            Cart.objects.create(
                client=self,
                product=product,
                number=number
            )

    # 购物车减少商品
    def cart_sub(self, product):
        cart = Cart.objects.filter(client=self, product=product).first()
        if cart:
            if cart.number == 1:
                cart.delete() # TODO 考虑是否是硬删除
            else:
                cart.number -= 1
                cart.save()

    # 购物车删除商品
    def cart_del(self, product):
        Cart.objects.filter(client=self, product=product).delete()

    class Meta:
        verbose_name = verbose_name_plural = '客户'

    def __str__(self):
        return '%s:%s' % (self.uid, self.nickname)


class Business(Base):

    name =  models.CharField('名称', max_length=200, blank=True)
    logo = models.CharField('LOGO', max_length=200, blank=True, null=True)
    desc = models.CharField('描述', max_length=200, blank=True)

    config = {
        'create': ['name'],
        'search': ['name', 'desc'],
        'default': ['id', 'name', 'logo', 'desc'],
        'detail': [],
        'privacy': ['created', 'updated'],
    }

    class Meta:
        verbose_name = verbose_name_plural = '商户'

    def __str__(self):
        return self.name


class Categorie(Base):
    """一级类目"""

    name =  models.CharField('名称', max_length=200, blank=True)

    config = {
        'create': ['name'],
        'search': ['name'],
        'default': ['id', 'name'],
        'detail': [],
        'privacy': ['created', 'updated'],
    }

    class Meta:
        verbose_name = verbose_name_plural = '一级类目'

    def __str__(self):
        return self.name


class SubCategorie(Base):
    """二级类目"""

    categorie = models.ForeignKey(Categorie, models.CASCADE, verbose_name='一级类目')
    name =  models.CharField('名称', max_length=200, blank=True)

    config = {
        'create': ['categorie', 'name'],
        'search': ['name'],
        'default': ['id', 'name'],
        'detail': ['categorie'],
        'privacy': ['created', 'updated'],
    }

    class Meta:
        verbose_name = verbose_name_plural = '二级类目'

    def __str__(self):
        return self.name


class ProductMeta(Base):
    """元商品"""

    business = models.ForeignKey(Business, models.CASCADE, verbose_name='商户')
    categorie = models.ForeignKey(Categorie, models.CASCADE, verbose_name='一级类目')
    sub_categorie = models.ForeignKey(SubCategorie, models.CASCADE, verbose_name='二级类目')
    name = models.CharField('名称', max_length=200, blank=True)
    video = models.CharField('视频', max_length=200, blank=True)
    images = models.CharField('图片', max_length=200, blank=True)
    desc = models.CharField('描述', max_length=200, blank=True)
    detial = models.TextField('图文详情')
    sold_num = models.IntegerField('总销量', default=0)

    status = models.CharField('状态', max_length=200, blank=True)

    config = {
        'create': ['business', 'categorie', 'sub_categorie', 'name'],
        'search': ['name', 'desc'],
        'default': ['id', 'business', 'categorie', 'sub_categorie', 'name', 'images', 'desc', 'sold_num'],
        'detail': ['video', 'detial'],
        'privacy': ['created', 'updated'],
    }

    class Meta:
        verbose_name = verbose_name_plural = '元商品'

    def __str__(self):
        return self.name


class Product(Base):
    """商品 SKU"""

    product_meta = models.ForeignKey(ProductMeta, models.CASCADE, verbose_name='元商品')
    # TODO 规格名称
    name = models.CharField('覆盖名称', max_length=200, blank=True)
    video = models.CharField('覆盖视频', max_length=200, blank=True)
    images = models.CharField('覆盖图片', max_length=200, blank=True)
    desc = models.CharField('覆盖描述', max_length=200, blank=True)

    price = models.IntegerField('价格(分)', default=0)
    origin_price = models.IntegerField('划线价(分)', default=0)

    stock = models.IntegerField('库存', default=0)
    sold_num = models.IntegerField('销量', default=0)

    status = models.CharField('状态', max_length=200, blank=True)

    config = {
        'create': ['product_meta', 'name'],
        'search': ['name', 'desc'],
        'default': ['id', 'product_meta', 'name', 'images', 'desc', 'price', 'origin_price'],
        'detail': ['video', 'stock', 'sold_num', 'status'],
        'privacy': ['created', 'updated'],
    }

    class Meta:
        verbose_name = verbose_name_plural = '元商品'

    def __str__(self):
        return self.name


class CouponMeta(Base):
    """元优惠券"""

    name = models.CharField('名称', max_length=200, blank=True)
    desc = models.CharField('描述', max_length=200, blank=True)

    at_least = models.IntegerField('满减额(分)', default=0)
    value = models.IntegerField('优惠券面额(分)', default=0)

    quota = models.IntegerField('用户限领个数', default=0)
    total = models.IntegerField('总数', default=0)
    count = models.IntegerField('当前已领取', default=0)

    range_type = models.CharField('可用范围类型', max_length=200) # PART:指定商品 ALL:全部商品

    type = models.CharField('类型', max_length=200) # 时间段/固定时长
    fixed_term = models.IntegerField('领取后 N 天可用', default=0)
    start_at = models.DateTimeField('可用时间')
    end_at = models.DateTimeField('结束时间')

    status = models.CharField('状态', max_length=200, blank=True)

    config = {
        'create': ['name'],
        'search': ['name', 'desc'],
        'default': ['id', 'desc', 'name', 'at_least', 'value'],
        'detail': ['quota', 'total', 'count', 'type', 'fixed_term', 'start_at', 'end_at'],
        'privacy': ['status', 'created', 'updated'],
    }

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = verbose_name_plural = '元优惠券'


class CouponMetaProductLine(Base):
    """元优惠券可用商品"""
    
    coupon_meta = models.ForeignKey(CouponMeta, models.CASCADE, verbose_name='元优惠券')
    product = models.ForeignKey('ProductMeta', models.CASCADE, verbose_name='元商品')

    config = {
        'create': ['coupon_meta', 'product'],
        'search': ['coupon_meta__name'],
        'default': ['id', 'coupon_meta', 'product'],
        'detail': [],
        'privacy': ['created', 'updated'],
    }

    def __str__(self):
        return self.coupon_meta.name

    class Meta:
        verbose_name = verbose_name_plural = '元优惠券可用商品'


class Coupon(Base):
    """优惠券"""

    coupon_meta = models.ForeignKey(CouponMeta, models.CASCADE, verbose_name='元优惠券')
    at_least = models.IntegerField('满减额(分)', default=0)
    value = models.IntegerField('优惠券面额(分)', default=0)

    start_at = models.DateTimeField('可用时间')
    end_at = models.DateTimeField('结束时间')

    status = models.CharField('状态', max_length=200, blank=True)

    config = {
        'create': [],
        'search': ['coupon_meta__name'],
        'default': ['id', 'coupon_meta', 'at_least', 'value'],
        'detail': ['start_at', 'end_at'],
        'privacy': ['status', 'created', 'updated'],
    }

    def __str__(self):
        return self.coupon_meta.name

    class Meta:
        verbose_name = verbose_name_plural = '优惠券'


class Order(Base):
    """订单"""

    status_choices = (
        ('待付款', '待付款'),
        ('待发货', '待发货'),
        ('待收货', '待收货'),

        ('已完成', '已完成'),
        ('已退货', '已退货'),
        ('已取消', '已取消'),
    )
    client = models.ForeignKey(Client, models.CASCADE, verbose_name='客户')
    num = models.CharField('单号', max_length=100)
    price = models.IntegerField('价格', default=0)
    real_price = models.IntegerField('实付价格', default=0)
    points = models.IntegerField('积分', default=0, blank=True)
    desc = models.CharField('描述', max_length=200)

    coupon = models.ForeignKey(Coupon, models.CASCADE, verbose_name='代金券', null=True, blank=True)

    fullname = models.CharField('收货姓名', max_length=100, blank=True)
    phone = models.CharField('收货手机号', max_length=100, blank=True)
    address = models.CharField('收货地址', max_length=100, blank=True)
    remark = models.CharField('备注', max_length=200, blank=True)

    status = models.IntegerField('状态', default='待付款', choices=status_choices)

    config = {
        'create': ['client', 'num'],
        'search': ['num', 'desc', 'fullname', 'phone', 'address', 'remark'],
        'default': ['id', 'client', 'num', 'price', 'real_price', 'points'],
        'detail': ['start_at', 'end_at'],
        'privacy': ['status', 'created', 'updated'],
    }

    def __str__(self):
        return '%s:%s' % (self.num, self.fullname)

    class Meta:
        verbose_name = verbose_name_plural = '商城订单'


class OrderLine(Base):
    """订单内容"""

    order = models.ForeignKey(Order, models.CASCADE, verbose_name='订单')
    product = models.ForeignKey(Product, models.CASCADE, verbose_name='商品')
    number = models.IntegerField('数量', default=0)

    config = {
        'create': ['order', 'product'],
        'search': ['order__num'],
        'default': ['id', 'order', 'product', 'number'],
        'detail': [],
        'privacy': ['created', 'updated'],
    }

    def __str__(self):
        return '%s:' % (self.order.num, self.product.name)

    class Meta:
        verbose_name = verbose_name_plural = '订单内容'


class Bill(Base):
    """账单"""

    client = models.ForeignKey(Client, models.CASCADE, verbose_name='客户')
    desc = models.CharField('描述', max_length=200, blank=True)
    price = models.IntegerField('金额(分)', default=0)
    order = models.ForeignKey(Order, models.CASCADE, verbose_name='订单', null=True, blank=True)

    config = {
        'create': [],
        'search': ['desc'],
        'default': ['id', 'client', 'desc', 'price', 'order'],
        'detail': [],
        'privacy': ['created', 'updated'],
    }

    def __str__(self):
        return self.client.nickname

    class Meta:
        verbose_name = verbose_name_plural = '账单'


class Cart(Base):
    """购物车"""

    client = models.ForeignKey(Client, models.CASCADE, verbose_name='客户')
    product = models.ForeignKey(Product, models.CASCADE, verbose_name='商品')
    number = models.IntegerField('数量', default=1)

    config = {
        'create': ['client', 'product'],
        'search': ['product__name'],
        'default': ['id', 'product', 'number'],
        'detail': ['client'],
        'privacy': ['created', 'updated'],
    }

    def __str__(self):
        return '%s:%s' % (self.client.nickname, self.product.name)

    class Meta:
        verbose_name = verbose_name_plural = '购物车'
