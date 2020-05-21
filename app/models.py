from __future__ import unicode_literals

from django.db import models
from django.contrib.auth import models as auth_models
from libs.tools import Base, SoftDeletionManager
from core.const import GENDER_MALE, GENDER_FEMALE


class UserManager(auth_models.UserManager, SoftDeletionManager):
    pass


class User(Base, auth_models.AbstractUser):

    GENDER_CHOICES = (
        (GENDER_MALE, "男"),
        (GENDER_FEMALE, "女"),
    )

    shop = models.ForeignKey('shop.Shop', models.CASCADE, null=True, db_constraint=False)
    name = models.CharField("姓名", max_length=32, null=True)
    phone = models.CharField("手机号", max_length=12, null=True)
    avatar = models.CharField("头像", max_length=100, null=True)
    ip = models.CharField("IP地址", max_length=32, null=True)
    gender = models.SmallIntegerField("性别", choices=GENDER_CHOICES, default=GENDER_MALE)

    reg_id = models.CharField("推送id", max_length=512, null=True, blank=True)

    objects = UserManager()

    config = {
        'create': [],
        'search': [],
        'default': [],
        'detail': [],
        'privacy': ['created', 'updated'],
    }

    class Meta:
        verbose_name = '用户'


class WxUser(models.Model):

    openid = models.CharField(max_length=200)
    nickname = models.CharField('昵称', max_length=200)
    headimgurl = models.CharField('头像地址', max_length=200)
    country = models.CharField('国家', max_length=200)
    province = models.CharField('省', max_length=200)
    city = models.CharField('城市', max_length=200)
    sex = models.CharField('性别', max_length=200)
    language = models.CharField('语言', max_length=200)
    privilege = models.CharField('权限', max_length=200)

    expires_at = models.CharField('过期时间', max_length=200)
    subscribe = models.CharField('关注状态', max_length=200, blank=True, null=True)
    subscribe_time = models.CharField('关注时间', max_length=200, blank=True, null=True)
    unionid = models.CharField(max_length=200, blank=True, null=True)
    remark = models.CharField('备注', max_length=200, blank=True, null=True)
    groupid = models.CharField('分组ID', max_length=200, blank=True, null=True)
    tagid_list = models.CharField('标签ID列表', max_length=200, blank=True, null=True)
    created = models.DateTimeField('创建时间', auto_now_add=True)

    def __str__(self):
        return self.nickname
