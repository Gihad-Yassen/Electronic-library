# from django.contrib import admin
# from .models import *
# from django.contrib import admin
# from django.contrib.admin.options import ModelAdmin
# from django.contrib.admin.views.main import ChangeList
# from .models import Book, Category, Course

# class CustomModelAdmin(ModelAdmin):
#     def __init__(self, model, admin_site):
#         self.list_display = [field.name for field in model._meta.fields]

# admin.site.register(Book, CustomModelAdmin)
# admin.site.register(Category, CustomModelAdmin)
# admin.site.register(Course, CustomModelAdmin)


# admin.site.register(Book)
# admin.site.register(Category)
# admin.site.register(Course)

from django.contrib import admin
from .models import Book, Category, Course
from django.contrib.admin import ModelAdmin


class CustomModelAdmin(ModelAdmin):
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.list_display = [field.name for field in model._meta.fields]



admin.site.register(Book, CustomModelAdmin)
admin.site.register(Category, CustomModelAdmin)
admin.site.register(Course, CustomModelAdmin)

