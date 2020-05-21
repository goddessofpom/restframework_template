from django.contrib import admin
from app import models

for i in dir(models):
    k = getattr(models, i)
    if 'django.db.models.base' in str(type(k)):
        try:
            admin.site.register(k)
        except:
            pass
