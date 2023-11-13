from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    ingredient_name = filters.CharFilter(
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ('ingredient_name',)


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.BooleanFilter(
        field_name='in_favorites__user',
        method='filter_by_favorites'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='in_shopping_list__user',
        method='filter_by_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_in_shopping_cart', 'is_favorited')

    def filter_by_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(in_shopping_list__user=self.request.user)
        return queryset.exclude(in_shopping_list__user=self.request.user)

    def filter_by_favorites(self, queryset, name, value):
        if value:
            return queryset.filter(in_favorites__user=self.request.user)
        return queryset.exclude(in_favorites__user=self.request.user)
