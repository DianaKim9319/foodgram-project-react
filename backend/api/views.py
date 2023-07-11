from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.exceptions import ValidationError, MethodNotAllowed
from rest_framework.pagination import PageNumberPagination

from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import check_password
from django.http import FileResponse
from django.db.models import Count, Q

from users.models import CustomUser, Follow
from recipes.models import (Tag, Ingredient, Recipes,
                            Favorites, ShoppingList, IngredientsAmount)
from .serializers import (CustomUserSerializer, CurrentUserSerializer,
                          IngredientSerializer,
                          TagSerializer, RecipeSerializer,
                          SubscriptionPageSerializer)
from api.permissions import (AdminOrReadOnly, AuthorOrAdminOrReadOnly,
                             CustomUserCreatePermission)


class CustomUserViewSet(viewsets.ModelViewSet):
    permission_classes = [CustomUserCreatePermission]
    pagination_class = PageNumberPagination
    queryset = CustomUser.objects.all()

    def get_serializer_class(self):
        if self.action == 'me':
            return CurrentUserSerializer
        return CustomUserSerializer

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        if request.user.is_anonymous:
            return Response(
                {
                    'detail': 'Учетные данные не были предоставлены.'
                }, status=401
            )
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], )
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = get_object_or_404(CustomUser, email=email)

        if check_password(password, user.password):
            return Response(
                {
                    'message': 'Авторизация выполнена'
                }, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    'message': 'Неверный пароль'
                }, status=status.HTTP_401_UNAUTHORIZED
            )

    @action(detail=False, methods=['post'])
    def set_password(self, request):
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        user = request.user

        if check_password(current_password, user.password):
            user.set_password(new_password)
            user.save()
            return Response(
                {
                    'message': 'Пароль успешно обновлён.'
                }, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    'message': 'Неверный пароль.'
                }, status=status.HTTP_401_UNAUTHORIZED
            )

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='subscribe',
        permission_classes=(IsAuthenticated,)
    )
    def subscribe_unsubscribe(self, request, pk=None):
        user = request.user
        author = get_object_or_404(CustomUser, id=pk)

        if author is None:
            raise ValidationError({'error': ['Автор не существует.']})

        if request.method == 'POST':
            follow, created = Follow.objects.get_or_create(
                user=request.user,
                author=author
            )
            if created is not None:
                response_data = {
                    'email': user.email,
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_subscribed': True,
                    'recipes': [
                        {
                            'id': recipe.id,
                            'name': recipe.name,
                            'image': recipe.image.url,
                            'cooking_time': recipe.cooking_time
                        }
                        for recipe in author.recipes.all()
                    ],
                    'recipes_count': author.recipes.count()
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                raise ValidationError(
                    {'error': ['Вы уже подписаны на автора.']}
                )

        elif request.method == 'DELETE':
            follow = Follow.objects.filter(user=request.user, author=author)
            if follow is not None:
                follow.delete()
                response_data = {
                    'message': 'Вы успешно отписались от автора.'
                }
                return Response(
                    response_data,
                    status=status.HTTP_200_OK
                )
            else:
                raise ValidationError(
                    {'error': ['Вы не подписаны на автора.']}
                )

        raise MethodNotAllowed(request.method)

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


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)
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


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination
    permission_classes = (AuthorOrAdminOrReadOnly,)

    def get_queryset(self):
        queryset = self.queryset
        author = self.request.query_params.get('author')
        if author is not None:
            if author == 'me':
                queryset = queryset.filter(author=self.request.user)
            else:
                queryset = queryset.filter(author_id=author)

        tags = self.request.query_params.getlist('tags')
        if tags is not None and len(tags) > 0:
            q_objects = Q()
            for tag in tags:
                q_objects |= Q(tags__slug=tag)
            queryset = queryset.annotate(
                matched_tags=Count('tags', filter=q_objects))\
                .filter(matched_tags__gt=0
                        )

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
        recipe = get_object_or_404(Recipes, id=pk)
        if recipe is None:
            raise ValidationError({'error': ['Рецепт не найден.']})

        if request.method == 'POST':
            favorites, created = Favorites.objects.get_or_create(
                user=request.user, recipe=recipe
            )
            if created is not None:
                response_data = {
                    'id': recipe.id,
                    'name': recipe.name,
                    'image': recipe.image.url,
                    'cooking_time': recipe.cooking_time
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                raise ValidationError({'error': ['Рецепт уже в избранном.']})

        elif request.method == 'DELETE':
            favorites = (
                Favorites.objects
                .filter(user=request.user, recipe=recipe)
            )
            if favorites is not None:
                favorites.delete()
                response_data = {
                    'message': "Рецепт успешно удален из избранного."
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                raise ValidationError({'error': ['Рецепт не в избранном.']})

        raise MethodNotAllowed(request.method)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def shopping_list(self, request, pk=None):
        recipe = get_object_or_404(Recipes, id=pk)
        if recipe is None:
            raise ValidationError({'error': ['Рецепт не найден.']})

        if request.method == 'POST':
            shopping_list, created = ShoppingList.objects.get_or_create(
                user=request.user,
                recipes=recipe
            )
            if created is not None:
                response_data = {
                    'id': recipe.id,
                    'name': recipe.name,
                    'image': recipe.image.url,
                    'cooking_time': recipe.cooking_time
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                raise ValidationError(
                    {'error': ['Рецепт уже в списке покупок.']}
                )

        elif request.method == 'DELETE':
            shopping_list = ShoppingList.objects.filter(
                user=request.user,
                recipes=recipe
            )
            if shopping_list is not None:
                shopping_list.delete()
                response_data = {
                    'message': 'Рецепт успешно удален из списка покупок.'
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                raise ValidationError(
                    {'error': ['Рецепт не в списке покупок.']}
                )

        raise MethodNotAllowed(request.method)

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
            .values_list('recipes__pk', flat=True)
        )
        ingredients = IngredientsAmount.objects.filter(
            recipe__in=shopping_list
        )
        ingredient_totals = {}
        for ingredient in ingredients:
            name = ingredient.ingredient_name.name
            unit = ingredient.ingredient_name.measurement_unit
            amount = ingredient.amount

            if name in ingredient_totals:
                # Если ингредиент уже есть в списке, плюсум количество.
                ingredient_totals[name]['amount'] += amount
            else:
                # Если ингредиент новый, то добавляем его.
                ingredient_totals[name] = {'amount': amount, 'unit': unit}

        # Создаем временный файл TXT
        filename = 'shopping_list.txt'
        with open(filename, 'w', encoding='utf-8') as file:
            file.write('Ингредиент, Количество, Единица измерения:\n')
            for ingredient, data in ingredient_totals.items():
                line = f'- {ingredient}, {data["amount"]}, {data["unit"]}\n'
                file.write(line)

        # Создаем FileResponse,
        # открывая временный файл в режиме чтения байтов ("rb"),
        # и устанавливаем заголовок Content-Disposition,
        # чтобы указать имя файла для скачивания
        response = FileResponse(open(filename, 'rb'))
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
