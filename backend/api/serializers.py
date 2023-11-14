from django.utils.translation import gettext_lazy as _
from django.db import transaction
from rest_framework.serializers import (ModelSerializer,
                                        CharField,
                                        SerializerMethodField,
                                        PrimaryKeyRelatedField,
                                        IntegerField,
                                        ListField)
from djoser.serializers import (UserCreateSerializer,
                                UserSerializer)
from users.models import CustomUser
from recipes.models import (Recipe,
                            Ingredient,
                            Tag,
                            IngredientsAmount,)

from api.validators import ingredients_validator, cooking_time_validator
from api.mixins import IsSubscribedMixin, IngredienteMixin
from api.fields import Base64ImageField


class CurrentUserSerializer(UserSerializer, IsSubscribedMixin):
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


class CustomUserSerializer(UserCreateSerializer, IsSubscribedMixin):
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


class ShortRecipeSerializer(ModelSerializer):
    """Сериализатор для сокращенного вывода рецепта на странице подписок."""

    class Meta:
        model = Recipe
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
        # Cтанислав, добрый день. Если Вы читаете это сообщение,
        # то я не смогла найти Вас в пачке, а куратор мне так и не ответила.
        # Не удаётся применить правки, которые Вы посоветовали,
        # так как read_only_fields ждёт от меня list или turple.
        # Данную информацию я нашла в документации,
        # после нескольких попыток понять, почему у меня всё сломалось.:)

    @staticmethod
    def get_recipes_count(obj):
        return obj.recipes.all().count()


class TagSerializer(ModelSerializer):
    """Сериализатор для тэгов."""

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('__all__',)


class IngredientSearchSerializer(ModelSerializer):
    """Сериализатор для выбора ингредиентов из списка."""

    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('__all__',)


class IngredientSerializer(ModelSerializer):
    """Сериализатор для вывода информации об ингредиентах."""

    id = IntegerField(source='ingredient_name.id')
    name = CharField(source='ingredient_name.name')
    measurement_unit = CharField(source='ingredient_name.measurement_unit')

    class Meta:
        model = IngredientsAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientAddSerializer(ModelSerializer):
    """Сериализатор ингредиентов при создании рецепта."""

    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = IntegerField()

    class Meta:
        model = IngredientsAmount
        fields = ('id', 'amount')


class RecipeSerializer(ModelSerializer):
    """Сериализатор для рецептов."""

    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientSerializer(
        read_only=True, many=True, source='ingredients'
    )
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
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
            'in_favorited',
            'is_in_shopping_cart',
        )

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


class RecipeCreateSerializer(ModelSerializer, IngredienteMixin):
    """Сериализатор для создания рецептов."""

    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = CustomUserSerializer(read_only=True)
    ingredients = ListField(child=IngredientAddSerializer())
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def to_representation(self, instance):
        serializer = RecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        )
        return serializer.data

    def validate(self, data):
        user = self.context.get('request').user
        tags = data.get('tags')
        ingredients = data.get('ingredients')
        ingredients_validated = ingredients_validator(ingredients)
        cooking_time = data.get('cooking_time')
        cooking_time_validator(cooking_time)

        data.update(
            {
                'author': user,
                'tags': tags,
                'ingredients': ingredients_validated,
                'cooking_time': cooking_time,
            }
        )
        return data

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        self.ing_create_update(ingredients, IngredientsAmount, recipe)

        recipe.tags.set(tags_data)

        request = self.context['request']
        recipe.author = request.user
        return recipe

    @transaction.atomic
    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        instance = super().update(recipe, validated_data)

        if ingredients is not None:
            IngredientsAmount.objects.filter(recipe=recipe).delete()
            self.ing_create_update(ingredients, IngredientsAmount, instance)

        if tags_data is not None:
            instance.tags.clear()
            instance.tags.set(tags_data)

        return recipe
