from django.core.exceptions import ValidationError
from django.conf import settings

MIN_INGREDIENT_AMOUNT = settings.MIN_INGREDIENT_AMOUNT
MAX_INGREDIENT_AMOUNT = settings.MAX_INGREDIENT_AMOUNT
MIN_COOKING_TIME = settings.MIN_COOKING_TIME
MAX_COOKING_TIME = settings.MAX_COOKING_TIME


def ingredients_validator(ingredients):
    """
    Валидирует список ингредиентов.

    Проверяет минмальное и максимальное количество ингредиентов и что
    ингредиенты не повторяются.
    """
    ingredient_names = set()

    for ingredient in ingredients:
        amount = ingredient['amount']
        name = ingredient['id']

        if name in ingredient_names:
            raise ValidationError('Ингредиенты не должны повторяться.')

        ingredient_names.add(name)

        if not MIN_INGREDIENT_AMOUNT <= amount <= MAX_INGREDIENT_AMOUNT:
            raise ValidationError({
                'amount': [
                    'Количество ингредиента должно быть от {} до {}.'.format(
                        MIN_INGREDIENT_AMOUNT, MAX_INGREDIENT_AMOUNT
                    )
                ]
            })

    return ingredients


def cooking_time_validator(cooking_time):
    """
    Валидирует суммарное время готовки.

    Проверяет минимальное и максимальное время готовки.
    """
    if not MIN_COOKING_TIME <= cooking_time <= MAX_COOKING_TIME:
        raise ValidationError({
            'cooking_time': [
                'Время готовки должно быть от {} до {} минут.'.format(
                    MIN_COOKING_TIME, MAX_COOKING_TIME
                )
            ]
        })
