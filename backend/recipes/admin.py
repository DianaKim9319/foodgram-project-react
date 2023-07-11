from django.contrib import admin
from django.db import models
from .models import Recipes, Ingredient, Tag, IngredientsAmount


class AdminPermissions(admin.ModelAdmin):
    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True


class IngredientsAmountInline(admin.TabularInline):
    model = IngredientsAmount


@admin.register(Recipes)
class RecipesAdmin(AdminPermissions):
    list_display = ('name', 'author', 'favorite_count')
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name', 'author__username')
    inlines = [IngredientsAmountInline]
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
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(AdminPermissions):
    list_display = ('name',)
    list_filter = ('name',)
