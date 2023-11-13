from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    """Кастомный фильтр для рецептов.
    Для вкладок "Избранное, "Корзина" и тегов."""
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        label='tags',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.BooleanFilter(
        label='Favorited',
        method='get_is_favorited',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        label='ShoppingCart',
        method='get_is_in_shopping_cart',
    )

    class Meta:
        model = Recipe
        fields = ('author', 'is_favorited', 'tags', 'is_in_shopping_cart', )

    def get_is_favorited(self, queryset, value):
        if value:
            return queryset.filter(in_favorites__user=self.request.user)
        return queryset.all()

    def get_is_in_shopping_cart(self, queryset, value):
        if value:
            return queryset.filter(in_shopping_list__user=self.request.user)
        return queryset.all()
