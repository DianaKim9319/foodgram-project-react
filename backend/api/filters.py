from django_filters import FilterSet, CharFilter, BooleanFilter
from recipes.models import Recipe


class RecipeFilter(FilterSet):
    author = CharFilter(method='filter_by_author')
    tags = CharFilter(method='filter_by_tags')
    is_in_shopping_cart = BooleanFilter(method='filter_by_shopping_cart')
    is_favorited = BooleanFilter(method='filter_by_favorited')

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_in_shopping_cart', 'is_favorited']

    def filter_by_author(self, queryset, name, value):
        if value == 'me':
            return queryset.filter(author=self.request.user)
        return queryset.filter(author_id=value)

    def filter_by_tags(self, queryset, name, value):
        return queryset.filter(tags__slug__in=value)

    def filter_by_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(in_shopping_list__user=self.request.user)
        return queryset.exclude(in_shopping_list__user=self.request.user)

    def filter_by_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(in_favorites__user=self.request.user)
        return queryset.exclude(in_favorites__user=self.request.user)
