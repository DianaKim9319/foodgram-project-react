from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import PermissionDenied
from rest_framework.serializers import (ModelSerializer,
                                        CharField,
                                        SerializerMethodField,
                                        PrimaryKeyRelatedField,
                                        IntegerField,
                                        ListField)

from djoser.serializers import (UserCreateSerializer,
                                UserSerializer)

from users.models import CustomUser, Follow
from recipes.models import (Recipe,
                            Ingredient,
                            Tag,
                            IngredientsAmount,
                            Favorite)
from .validators import tags_validator, ingredients_validator
from .mixins import IsSubscribedMixin, IngredienteMixin
from .fields import Base64ImageField


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

    def to_representation(self, instance):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return super().to_representation(instance)
        else:
            raise PermissionDenied("Учетные данные не были предоставлены")


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

    @staticmethod
    def get_recipes_count(obj: CustomUser):
        return obj.recipes.all().count()


class TagSerializer(ModelSerializer):
    """Сериализатор для тэгов."""

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('__all__',)


class IngredientSearchSerializer(ModelSerializer):
    """Сериализатор для выбора ингредиентов из списка"""
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('__all__',)


class IngredientSerializer(ModelSerializer):
    """Сериализатор для вывода информации об ингредиентах"""
    amount = SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_amount(self, obj):
        ingredients_amount = obj.recipe.filter(ingredient_name=obj).first()
        return ingredients_amount.amount


class IngredientAddSerializer(ModelSerializer):
    """Сериализатор ингредиентов при создании рецепта"""

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
        read_only=True, many=True
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
        tags_validated = tags_validator(tags, Tag)
        ingredients_validated = ingredients_validator(ingredients)

        data.update(
            {
                'author': user,
                'tags': tags_validated,
                'ingredients': ingredients_validated,
            }
        )
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        self.ing_create_update(ingredients, IngredientsAmount, recipe)

        recipe.tags.set(tags_data)

        request = self.context['request']
        recipe.author = request.user
        return recipe

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

        instance.save()
        return recipe


class FavoriteSerializer(ModelSerializer):
    """Сериализатор модели избранного."""
    class Meta:
        model = Favorite
        fields = ['id', 'name', 'image', 'cooking_time']

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return Follow.objects.filter(
            author=obj.author, user=request.user
        ).exists()

    @staticmethod
    def get_recipes(obj):
        author = obj.author
        recipes = Recipe.objects.filter(author=author)
        serializer = ShortRecipeSerializer(recipes, many=True)
        return serializer.data

    @staticmethod
    def get_recipes_count(obj):
        author = obj.author
        return author.recipes.count()
