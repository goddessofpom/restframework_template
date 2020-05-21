from django.contrib import admin
from backbone import models

class BaseAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated', 'deleted')

for i in dir(models):
    k = getattr(models, i)
    if 'django.db.models.base' in str(type(k)):
        try:
            admin.site.register(k, BaseAdmin)
        except:
            pass
