from django.core.exceptions import ValidationError


def ingredients_validator(ingredients):
    """
    Валидирует список ингредиентов.

    Проверяет, что каждый ингредиент имеет положительное количество и что
    ингредиенты не повторяются.
    """
    ingredient_names = set()

    for ingredient in ingredients:
        amount = ingredient['amount']
        name = ingredient['id']

        if int(amount) <= 0:
            raise ValidationError(
                {
                    'amount':
                    ['Убедитесь, что это значение больше либо равно 1.']
                }
            )
        if name in ingredient_names:
            raise ValidationError('Ингредиенты не должны повторяться.')

        ingredient_names.add(name)

    return ingredients
