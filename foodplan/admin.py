from django.contrib import admin

from foodplan.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass

