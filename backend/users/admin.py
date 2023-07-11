from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_active'
    )
    list_filter = ('email', 'username', 'is_active')
    search_fields = (
        'username',
        'email',
    )
    save_on_top = True

    actions = ['block_users', 'activate_users']

    def change_password(self, request, user_):
        return self.password_change_view(request, user_)

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def block_users(self, request, queryset):
        queryset.update(is_active=False)
    block_users.short_description = 'Заблокировать выбранных пользователей'

    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
    activate_users.short_description = 'Активировать выбранных пользователей'
