from django.http import HttpResponse
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from djoser.views import UserViewSet
from djoser.serializers import SetPasswordSerializer

from users.models import CustomUser, Follow
from recipes.models import (Tag, Ingredient, Recipe,
                            Favorite, ShoppingList, IngredientsAmount)
from .serializers import (CustomUserSerializer,
                          IngredientSearchSerializer,
                          TagSerializer, RecipeSerializer, RecipeCreateSerializer,
                          SubscriptionPageSerializer, ShortRecipeSerializer)
from .mixins import AddDeleteMixin
from .permissions import AuthorOrReadOnly


class BasePermissionViewSet(viewsets.ModelViewSet):
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()


class CustomUserViewSet(UserViewSet, AddDeleteMixin):
    pagination_class = PageNumberPagination
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_serializer_class(self):
        if self.action == 'set_password':
            return SetPasswordSerializer
        return CustomUserSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='subscribe',
        permission_classes=(IsAuthenticated,),
    )
    def subscribe_unsubscribe(self, request, id=None):
        author = get_object_or_404(CustomUser, id=id)

        return self.add_delete(
            request=request,
            model=Follow,
            serializer_class=SubscriptionPageSerializer,
            error_message={
                'post': 'Вы уже подписаны на автора.',
                'delete': 'Вы не подписаны на автора.'
            },
            success_message='Вы успешно отписались от автора.',
            item=author,
            field_name='author'
        )

    @action(
        detail=False,
        methods=['get'],
        url_path='subscriptions',
        permission_classes=(IsAuthenticated,)
    )
    def my_subscriptions(self, request):
        user = request.user
        subscriptions = CustomUser.objects.filter(following__user=user)
        paginated_subscriptions = self.paginate_queryset(subscriptions)
        serializer = (
            SubscriptionPageSerializer(
                paginated_subscriptions,
                many=True,
                context={'request': request}
            )
        )
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(BasePermissionViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSearchSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name__istartswith']
    search_param = "name"
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get(self.search_param)

        if name is not None:
            queryset = queryset.filter(name__istartswith=name)
            start_names = queryset.values_list('name', flat=True)
            queryset = queryset.union(
                self.queryset.filter(name__icontains=name)
                .exclude(name__in=start_names)
            )

        return queryset


class TagViewSet(BasePermissionViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet, AddDeleteMixin):
    queryset = Recipe.objects.all()
    pagination_class = PageNumberPagination
    permission_classes = (AuthorOrReadOnly,)
    serializer_class = RecipeSerializer

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeCreateSerializer

    def get_queryset(self):
        queryset = self.queryset
        author = self.request.query_params.get('author')
        if author is not None:
            if author == 'me':
                queryset = queryset.filter(author=self.request.user)
            else:
                queryset = queryset.filter(author_id=author)

        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags)

        if not self.request.user.is_anonymous:
            is_in_cart = self.request.query_params.get(
                'is_in_shopping_cart'
            )
            if is_in_cart == '1':
                queryset = queryset.filter(
                    in_shopping_list__user=self.request.user
                )
            elif is_in_cart == '0':
                queryset = queryset.exclude(
                    in_shopping_list__user=self.request.user
                )

            is_favorite = self.request.query_params.get(
                'is_favorited'
            )
            if is_favorite == '1':
                queryset = queryset.filter(
                    in_favorites__user=self.request.user
                )
            elif is_favorite == '0':
                queryset = queryset.exclude(
                    in_favorites__user=self.request.user
                )

        queryset = queryset.order_by('-pub_date')

        return queryset.distinct()

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='favorite',
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        return self.add_delete(
            request=request,
            model=Favorite,
            serializer_class=ShortRecipeSerializer,
            error_message={
                'post': 'Рецепт уже в избранном.',
                'delete': 'Рецепт не в избранном.'
            },
            success_message='Рецепт успешно удален из избранного.',
            item=recipe,
            field_name='recipe'
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def shopping_list(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        return self.add_delete(
            request=request,
            model=ShoppingList,
            serializer_class=ShortRecipeSerializer,
            error_message={
                'post': 'Рецепт уже в списке покупок.',
                'delete': 'Рецепт не в списке покупок.'
            },
            success_message='Рецепт успешно удален из списка покупок.',
            item=recipe,
            field_name='recipe'
        )

    @action(
        methods=['get'],
        detail=False,
        url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart_list(self, request):
        user = request.user
        if not user.shopping_list.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        shopping_list = (
            ShoppingList.objects
            .filter(user=user)
            .values_list('recipe__pk', flat=True)
        )
        ingredients = (
            IngredientsAmount.objects
            .filter(recipe__in=shopping_list)
            .values('ingredient_name__name', 'ingredient_name__measurement_unit')
            .annotate(sum_amount=Sum('amount'))
        )
        ingredient_totals = {
            ingredient['ingredient_name__name']: {
                'amount': ingredient['sum_amount'],
                'unit': ingredient['ingredient_name__measurement_unit']
            }
            for ingredient in ingredients
        }

        # Создаем динамический файл TXT
        filename = 'shopping_list.txt'
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
        response.write('Ингредиент, Количество, Единица измерения:\n')
        for ingredient, data in ingredient_totals.items():
            line = f'- {ingredient}, {data["amount"]}, {data["unit"]}\n'
            response.write(line)
        return response
