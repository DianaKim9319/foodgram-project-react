from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
    )
    is_favorite = filters.BooleanFilter(
        field_name='in_favorites__user',
        method='filter_by_favorites'
    )
    is_in_cart = filters.BooleanFilter(
        field_name='in_shopping_list__user',
        method='filter_by_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorite', 'is_in_cart',)

    def filter_by_favorites(self, queryset, value):
        if value:
            return queryset.filter(in_favorites__user=self.request.user)
        return queryset.exclude(in_favorites__user=self.request.user)

    def filter_by_shopping_cart(self, queryset, value):
        if value:
            return queryset.filter(in_shopping_list__user=self.request.user)
        return queryset.exclude(in_shopping_list__user=self.request.user)
