from django.core.exceptions import ValidationError


def tags_validator(tags, model):
    if not tags:
        raise ValidationError(
            {'tags': ['Обязательное поле.']}
        )

    tags_exist = model.objects.filter(name__in=tags).exists()

    if not tags_exist:
        raise ValidationError(
            {'tags': 'Такого тэга нет в базе'}
        )

    return tags


def ingredients_validator(ingredients):
    if not ingredients:
        raise ValidationError(
            {'ingredients': ['Обязательное поле.']}
        )
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
