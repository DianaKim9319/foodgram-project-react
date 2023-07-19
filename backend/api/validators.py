from django.core.exceptions import ValidationError


def ingredients_validator(ingredients):
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
