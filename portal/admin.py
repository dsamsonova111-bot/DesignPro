from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Category, DesignRequest


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'full_name', 'email', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('full_name',)}),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(DesignRequest)
class DesignRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'user', 'created_at')
    list_filter = ('status', 'category')