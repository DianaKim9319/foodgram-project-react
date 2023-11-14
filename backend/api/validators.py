from django.core.exceptions import ValidationError
from foodgram.settings import (MIN_INGR_AMOUNT,
                               MAX_INGR_AMOUNT,
                               MAX_COOK_TIME,
                               MIN_COOK_TIME)


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

        if not MIN_INGR_AMOUNT <= amount <= MAX_INGR_AMOUNT:
            raise ValidationError({
                'amount': [
                    f'Количество ингредиента должно быть от {MIN_INGR_AMOUNT} '
                    f'до {MAX_INGR_AMOUNT}.'
                ]
            })

    return ingredients


def cooking_time_validator(cooking_time):
    """

    Проверяет минимальное и максимальное время готовки.
    """
    if not MIN_COOK_TIME <= cooking_time <= MAX_COOK_TIME:
        raise ValidationError({
            'cooking_time': [
                f'Время приготовления должно быть от {MIN_COOK_TIME} '
                f'до {MAX_COOK_TIME} минут.'
            ]
        })
