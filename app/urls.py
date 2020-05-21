from rest_framework.routers import DefaultRouter
from django.conf.urls import url, re_path, include
from app.views import upload_image

router = DefaultRouter()
router.trailing_slash = '[/]?'

urlpatterns = [
    url(r'^$', app.views.index),
    re_path('^upload', upload_image, name='upload_image'),
]
