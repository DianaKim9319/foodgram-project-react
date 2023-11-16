from django.contrib import admin
from django.db import models

from recipes.permissions import AdminPermissions
from recipes.models import (Recipe,
                            Ingredient,
                            Tag,
                            IngredientsAmount,
                            Favorite,
                            ShoppingList)


class IngredientsAmountInline(admin.TabularInline):
    model = IngredientsAmount


@admin.register(Recipe)
class RecipesAdmin(AdminPermissions):
    list_display = ('name', 'author', 'favorite_count')
    list_filter = ('tags',)
    search_fields = ('name', 'author__username')
    inlines = (IngredientsAmountInline,)
    readonly_fields = ('favorite_count',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            favorite_count=models.Count('in_favorites')
        )
        return queryset

    def favorite_count(self, obj):
        return obj.in_favorites.count()

    favorite_count.short_description = 'Число добавлений в избранное'


@admin.register(Ingredient)
class IngredientAdmin(AdminPermissions):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('measurement_unit',)


@admin.register(Tag)
class TagAdmin(AdminPermissions):
    list_display = ('name',)
    list_filter = ('name',)


@admin.register(IngredientsAmount)
class IngredientsAmountAdmin(AdminPermissions):
    list_display = ('recipe', 'ingredient_name', 'amount')
    search_fields = ('recipe__name', 'ingredient_name__name')
    list_filter = ('recipe__tags',)


@admin.register(Favorite)
class FavoriteAdmin(AdminPermissions):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'user__email', 'recipe__name')
    list_filter = ('recipe__tags',)


@admin.register(ShoppingList)
class ShoppingListAdmin(AdminPermissions):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'user__email', 'recipe__name')
    list_filter = ('recipe__tags',)
