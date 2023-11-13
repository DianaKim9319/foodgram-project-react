from django.http import HttpResponse
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
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
                          TagSerializer,
                          RecipeSerializer,
                          RecipeCreateSerializer,
                          SubscriptionPageSerializer,
                          ShortRecipeSerializer)
from .mixins import AddDeleteMixin
from .filters import RecipeFilter, IngredientFilter
from .permissions import AuthorOrReadOnly


class BasePermissionViewSet(viewsets.ModelViewSet):
    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        elif self.action in ('create', 'update', 'partial_update', 'destroy'):
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
        methods=('post', 'delete'),
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
        methods=('get',),
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
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_param = 'name'
    pagination_class = None


class TagViewSet(BasePermissionViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet, AddDeleteMixin):
    queryset = Recipe.objects.all().order_by('-id')
    pagination_class = PageNumberPagination
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeCreateSerializer

    @action(
        detail=True,
        methods=('post', 'delete'),
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
        methods=('post', 'delete'),
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
        methods=('get',),
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
            .values(
                'ingredient_name__name',
                'ingredient_name__measurement_unit'
            )
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
        response['Content-Disposition'] = 'attachment; filename={0}'.format(
            filename
        )
        response.write('Ингредиент, Количество, Единица измерения:\n')
        for ingredient, data in ingredient_totals.items():
            line = f'- {ingredient}, {data["amount"]}, {data["unit"]}\n'
            response.write(line)
        return response
