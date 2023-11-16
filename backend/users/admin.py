from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser, Follow
from users.permissions import AdminPermissions


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin, AdminPermissions):
    model = CustomUser
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_active'
    )
    list_filter = ('is_active',)
    search_fields = (
        'username',
        'email',
    )
    save_on_top = True

    actions = ['block_users', 'activate_users']

    def change_password(self, request, user_):
        return self.password_change_view(request, user_)

    def block_users(self, request, queryset):
        queryset.update(is_active=False)
    block_users.short_description = 'Заблокировать выбранных пользователей'

    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
    activate_users.short_description = 'Активировать выбранных пользователей'


class FollowAdmin(AdminPermissions):
    model = Follow
    list_display = ('user', 'author')
    list_filter = ('user', 'author')
