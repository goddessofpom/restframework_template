from django.forms.models import model_to_dict
from django.core.paginator import Paginator
from django.forms import ModelForm
from django.contrib.admin import widgets
from django.http import HttpResponse
from django.utils import timezone
from pywe_django import settings
from django.db.models.query import ModelIterable
from django.db.models import Q
from django.db import models
import datetime
import random
import json
import time


class SoftDeletionQuerySet(models.QuerySet):
    """修改 queryset 的 delete"""

    def delete(self):
        return super().update(deleted=timezone.now())

    def hard_delete(self):
        return super().delete()

    def search(self, keyword):

        if not keyword:
            return self
 
        filter = Q()
        for i in self.model.config['search']:
            filter |= Q(**{i + '__contains': keyword})

        return self.filter(filter)

    def paginator(self, limit=settings.PAGE_LIMIT):

        return Paginator(self, limit)


class SoftDeletionManager(models.Manager):
    """软删除之后默认排除 filter 条件"""

    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return SoftDeletionQuerySet(self.model).filter(deleted=None)
        return SoftDeletionQuerySet(self.model)

    def create(self, **kwargs):

        if len(self.model.config['create']):
            filter = Q()
            for i in self.model.config['create']:
                filter &= Q(**{i: kwargs[i]})

            if self.model.objects.filter(filter).exists():
                raise Exception(self.model._meta.verbose_name + '已存在')
        return super().create(**kwargs)

    def search(self, keyword):
 
        filter = Q()
        for i in self.model.config['search']:
            filter |= Q(**{i + '__contains': keyword})

        return self.filter(filter)


class Base(models.Model):

    created = models.DateTimeField('创建时间', auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField('更新时间', auto_now=True, null=True, blank=True)
    deleted = models.DateTimeField('删除时间', null=True, blank=True, editable=False)
    
    objects = SoftDeletionManager()
    all_objects = SoftDeletionManager(alive_only=False)

    def delete(self):
        self.deleted = timezone.now()
        self.save()

    def hard_delete(self):
        return super().delete()

    @classmethod
    def type_fields(cls, _type):
        fields = []
        for i in ['default', 'detail', 'privacy']:
            fields += cls.config[i]
            if _type == i:
                return fields

    def create_obj(self, _type):
        data = {
            'object_type': _type,
            'object_name': self._meta.model_name,
        }
        for i in self.type_fields(_type):
            value = getattr(self, i)
            if '.models.' in str(type(value)):
                value = getattr(value, _type, value)
            data[i] = value

        return data

    @property
    def default(self):
        return self.create_obj('default')

    @property
    def detail(self):
        return self.create_obj('detail')

    @property
    def privacy(self):
        return self.create_obj('privacy')

    @classmethod
    def form(cls, _type, extra_fields=[], attrs=[], exclude_fields=[]):

        class Form(ModelForm):

            def __init__(self, *args, **kwargs):
                super(Form, self).__init__(*args, **kwargs)
                for k,v in extra_fields:
                    self.fields[k] = v

                for key in self.fields:
                    field = self.fields[key]

                    if key in attrs:
                        for k, v in attrs[key].items():
                            field.widget.attrs[k] = v

                    _class = field.widget.attrs.get('class', '')
                    field.widget.attrs['class'] = 'form-control' + (_class and ' ') + _class
                    if 'DateTimeField' in str(field.__class__):
                        field.widget.attrs['data-mask-clearifnotmatch'] = "true"
                        field.widget.attrs['data-mask'] = "0000/00/00 00:00:00"
                        field.widget.attrs['placeholder'] = "0000/00/00 00:00:00"
           
            class Meta:
                model = cls._meta.model
                fields = cls.type_fields(_type)
                exclude = ['created', 'updated'] + exclude_fields

        return Form

    @classmethod
    def api_create(cls, request):

        data = {}
        for i in cls._meta.fields:
            if i.name in ['created', 'updated', 'deleted']:
                continue

            val = request.POST.get(i.name, False)
            if val:
                data[i.name] = val
            elif not i.null and not i.blank:
                return json_failed(403, '缺少参数: %s(%s)' % (i.verbose_name, i.name))

        cls.objects.create(**data)

        return json_success()

    @classmethod
    def api_delete(cls, request):

        id = request.GET.get('id', False)
        if not id:
            return json_failed(403, '缺少参数: ID(id)')

        cls.objects.get(id=id).delete()

        return json_success()

    @classmethod
    def api_list(cls, request):

        keyword = request.GET.get('keyword', '')
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', settings.PAGE_LIMIT))
        sort = request.GET.get('sort', '-id')

        p = cls.objects.all().search(keyword).order_by(sort).paginator(limit).page(page)

        return json_success({
            'page': page,
            'limit': limit,
            'keyword': keyword,
            'has_next': p.has_next(),
            'has_previous': p.has_previous(),
            'list': [i.default for i in p.object_list]
        })

    @classmethod
    def api_detail(cls, request):

        id = request.GET.get('id', False)
        if not id:
            return json_failed(403, '缺少参数: ID(id)')

        target = cls.objects.get(id=id)

        return json_success({
            'detail': target.detail
        })

    class Meta:
        abstract = True


def json_default(obj):
    """格式化 josn """

    if isinstance(obj, datetime.datetime):
        return (timezone.localtime(obj) if timezone.is_aware(obj) else obj).strftime('%Y-%m-%d %H:%M:%S')

    elif isinstance(obj, datetime.date):
        return obj.strftime('%Y-%m-%d')

    elif isinstance(obj, datetime.time):
        return obj.strftime('%H:%M:%S')

    elif isinstance(obj, models.QuerySet):
        if obj._iterable_class == ModelIterable:
            obj = obj.values()
        return tuple(obj)

    elif isinstance(obj, models.Model):

    # TODO 如果是外键返回对应 type 的 detail/default type

        return model_to_dict(obj)

    return json.JSONEncoder.default(None, obj)


def JSONResponse(data):
    """返回 json 格式"""

    return HttpResponse(
        json.dumps(data, default=json_default),
        content_type='application/json'
    )


def json_success(data={}):
    """返回成功的响应"""

    return JSONResponse({
        'errcode': 0,
        'msg': 'ok',
        'data': data
    })


def json_failed(errcode, msg, data={}):
    """返回失败的响应"""

    return JSONResponse({
        'errcode': errcode,
        'msg': msg,
        'data': data
    })


def generate_num():
    return str(int(time.time())) + str(random.randint(1000,9999))
