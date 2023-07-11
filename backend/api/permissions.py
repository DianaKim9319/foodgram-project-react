from rest_framework import permissions


class AuthorOrReadOnly(permissions.BasePermission):
    """
    Позволяет только авторизованным пользователям изменять объекты.
    Остальным разрешены только безопасные методы (GET, HEAD, OPTIONS).

    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class AdminOrReadOnly(permissions.BasePermission):
    """
    Позволяет только администраторам изменять объекты.
    Остальным разрешены только безопасные методы (GET, HEAD, OPTIONS).

    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_superuser


class AuthorOrAdminOrReadOnly(permissions.BasePermission):
    """
    Позволяет авторам объектов и администраторам изменять объекты.
    Остальным разрешены только безопасные методы (GET, HEAD, OPTIONS).

    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            or request.user.is_superuser
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_superuser
        )


class CustomUserCreatePermission(permissions.BasePermission):
    """
    Позволяет создание пользователей только при отправке HTTP POST-запроса.
    Остальным разрешены только безопасные методы (GET, HEAD, OPTIONS).

    """

    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        return (
            permissions.IsAuthenticatedOrReadOnly().has_permission(
                request, view
            )
        )
