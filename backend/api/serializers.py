import base64
from rest_framework.reverse import reverse
from rest_framework.serializers import (ModelSerializer, CharField,
                                        SerializerMethodField,
                                        ImageField)

from djoser.serializers import UserCreateSerializer, UserSerializer

from django.core.files.base import ContentFile
from django.db.models import F
from django.utils.translation import gettext_lazy as _

from users.models import CustomUser, Follow
from .validators import tags_validator, ingredients_validator
from recipes.models import Recipes, Ingredient, Tag, IngredientsAmount


class Base64ImageField(ImageField):
    """Кастомный тип поля для картинки."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            image_format, imgstr = data.split(';base64,')
            ext = image_format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class CurrentUserSerializer(UserSerializer):
    """Сериализатор текущего пользователя."""

    is_subscribed = SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        return False


class CustomUserSerializer(UserCreateSerializer):
    """Сериализатор модели пользователей."""

    password = CharField(write_only=True)
    is_subscribed = SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed',
        )
        error_messages = {
            'required': _('Обязательное поле.'),
        }

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        if request is not None:
            if request.method == 'POST' and request.path.endswith('/recipes/'):
                return fields
            elif request.method == 'POST' and request.path.endswith('/users/'):
                fields.pop('is_subscribed')
        return fields

    def create(self, validated_data: dict):
        user = CustomUser(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.following.filter(user=request.user).exists()
        return False


class FollowSerializer(ModelSerializer):
    """Сериализатор модели подписок."""

    author = SerializerMethodField()
    author_first_name = SerializerMethodField()
    author_last_name = SerializerMethodField()

    class Meta:
        model = Follow
        fields = ['author', 'author_first_name', 'author_last_name']

    def get_author(self, obj):
        request = self.context.get('request')
        return reverse('author-detail', args=[obj.author_id], request=request)

    @staticmethod
    def get_author_first_name(obj):
        return obj.author.first_name

    @staticmethod
    def get_author_last_name(obj):
        return obj.author.last_name


class ShortRecipeSerializer(ModelSerializer):
    """Сериализатор для сокращенного вывода рецепта на странице подписок."""

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionPageSerializer(CustomUserSerializer):
    """Сериализатор страницы подписок."""

    recipes = ShortRecipeSerializer(many=True, read_only=True)
    recipes_count = SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = ('__all__',)

    @staticmethod
    def get_recipes_count(obj: CustomUser):
        return obj.recipes.all().count()

    def get_is_subscribed(self, obj):
        is_subscribed = super().get_is_subscribed(obj)
        return is_subscribed


class TagSerializer(ModelSerializer):
    """Сериализатор для тэгов."""

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('__all__',)


class IngredientSerializer(ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('__all__',)


class RecipeSerializer(ModelSerializer):
    """Сериализатор для рецептов."""

    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = (
            'in_favorite',
            'is_in_shopping_cart',
        )
        error_messages = {
            'required': _('Обязательное поле.'),
        }

    def get_ingredients(self, obj):
        ingredients = obj.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('recipe__amount')
        )
        return ingredients

    def validate(self, data):
        user = self.context.get('request').user
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        tags_validated = tags_validator(tags, Tag)
        ingredients_validated = ingredients_validator(ingredients, Ingredient)

        data.update(
            {
                'author': user,
                'tags': tags_validated,
                'ingredients': ingredients_validated,
            }
        )
        return data

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.in_favorites.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.in_shopping_list.filter(user=user).exists()
        return False

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipes.objects.create(**validated_data)

        for ingredient, amount in ingredients_data.values():
            IngredientsAmount.objects.create(
                recipe=recipe,
                ingredient_name=ingredient,
                amount=amount
            )

        recipe.tags.set(tags_data)

        request = self.context['request']
        recipe.author = request.user
        recipe.save()

        return recipe

    def update(self, recipe, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe.name = validated_data.get('name', recipe.name)
        recipe.text = validated_data.get('text', recipe.text)
        recipe.cooking_time = validated_data.get(
            'cooking_time', recipe.cooking_time
        )
        recipe.image = validated_data.get('image', recipe.image)

        if ingredients_data is not None:
            recipe.ingredients.clear()
            for ingredient, amount in ingredients_data.values():
                IngredientsAmount.objects.create(
                    recipe=recipe,
                    ingredient_name=ingredient,
                    amount=amount
                )

        if tags_data is not None:
            recipe.tags.clear()
            recipe.tags.set(tags_data)

        recipe.save()
        return recipe
