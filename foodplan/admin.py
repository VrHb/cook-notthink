from django.contrib import admin
from .models import *


admin.site.register(Dish)
admin.site.register(Ingridients)
admin.site.register(DishType)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass