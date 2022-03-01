from django.contrib import admin
from .models import *
from import_export.admin import ImportExportActionModelAdmin


class imp(ImportExportActionModelAdmin):
    pass


# Register your models here.
admin.site.register(contact, imp)
admin.site.register(seller, imp)
admin.site.register(books, imp)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(Order)

