from django.contrib import admin
from .models import *
from import_export import resources
from import_export.admin import ImportExportModelAdmin


class DishAdminResource(resources.ModelResource):

    class Meta:
        model = Dish
        exclude = ('id')
        widgets = None
        import_id_fields = ('title',)


@admin.register(Dish)
class DishAdmin(ImportExportModelAdmin):
   resource_class = DishAdminResource
   list_display = ['image', 'title', 'description', 'dishtype', 'ingridients', 'calories']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass