from django.db import models
from users.models import CustomUser


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название тега',
        max_length=50,
        unique=True,
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Tag Slug',
        max_length=50,
        unique=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['id']


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=300,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=50,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit'
            )]

    def __str__(self):
        return f"{self.name} {self.measurement_unit}"


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser,
        verbose_name='Автор рецепта',
        related_name='recipes',
        on_delete=models.SET_NULL,
        null=True,
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=150,
    )
    image = models.ImageField(
        verbose_name='Фото блюда',
        upload_to='recipes/images/',
        default=None,
    )
    text = models.TextField(
        verbose_name='Текстовое описание рецепта',
        max_length=3000,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        related_name='recipes',
        through='recipes.IngredientsAmount'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'author'],
                name='unique_name_author'
            )]

    def __str__(self):
        return self.name


class IngredientsAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='ingredientsamount_set',
        on_delete=models.CASCADE,
    )
    ingredient_name = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        related_name='recipe',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=0,
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Количество ингридиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient_name'],
                name='unique_recipe_ingredient',
            ),
        ]

    def __str__(self):
        return f'{self.amount} {self.ingredient_name}'


class Favorite(models.Model):
    user = models.ForeignKey(
        CustomUser,
        verbose_name='Пользователь',
        related_name='favorites',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Избранные рецепты',
        related_name='in_favorites',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Список избранного'
        verbose_name_plural = 'Списки избранного'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_favorites_recipe_user',
            ),
        ]

    def __str__(self):
        return f'{self.user}. {self.recipe}'


class ShoppingList(models.Model):
    user = models.ForeignKey(
        CustomUser,
        verbose_name='Пользователь',
        related_name='shopping_list',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепты в корзине',
        related_name='in_shopping_list',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_shopping_list_recipe_user',
            ),
        ]

    def __str__(self):
        return f'{self.user}. {self.recipe}'
