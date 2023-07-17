from django.core.exceptions import ValidationError


def ingredients_validator(ingredients):
    for ingredient in ingredients:
        amount = ingredient['amount']

        if int(amount) <= 0:
            raise ValidationError(
                {
                    'amount':
                    ['Убедитесь, что это значение больше либо равно 1.']
                }
            )

    return ingredients
