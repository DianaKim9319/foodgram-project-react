from django.core.exceptions import ValidationError


def tags_validator(tags, model):
    if not tags:
        raise ValidationError(
            {'tags': ['Обязательное поле.']}
        )

    tags_exist = model.objects.filter(id__in=tags).exists()

    if not tags_exist:
        raise ValidationError(
            {'tags': 'Такого тэга нет в базе'}
        )

    return tags


def check_and_add_ingredients(model, validated_ingredients):
    ing_data = model.objects.filter(pk__in=validated_ingredients.keys())
    for ing in ing_data:
        validated_ingredients[ing.pk] = (ing, validated_ingredients[ing.pk])


def ingredients_validator(ingredients, model):
    if not ingredients:
        raise ValidationError(
            {'ingredients': ['Обязательное поле.']}
        )

    ingredient_ids = [ing['id'] for ing in ingredients]

    ingredients_exist = set(
        model.objects.filter(id__in=ingredient_ids)
        .values_list('id', flat=True)
    )

    miss_ing = set(ingredient_ids) - set(ingredients_exist)
    if miss_ing:
        raise ValidationError(
            {
                'ingredients':
                f'Ингредиент {", ".join(str(ing_id) for ing_id in miss_ing)} '
                f'отсутствует в базе'
            }
        )

    validated_ingredients = {}
    for ingredient_data in ingredients:
        if not (
                isinstance(ingredient_data['amount'], int)
                or ingredient_data['amount'].isdigit()
        ):
            raise ValidationError(
                {
                    'amount': [
                        'Убедитесь, что это значение является целым числом.'
                    ]
                }
            )

        ingredient_id = ingredient_data.get('id')
        amount = int(ingredient_data.get('amount'))

        if amount <= 0:
            raise ValidationError(
                {
                    'amount': [
                        'Убедитесь, что это значение больше либо равно 1.'
                    ]
                }
            )

        validated_ingredients[ingredient_id] = amount

    if not validated_ingredients:
        raise ValidationError('Неверный формат ингредиентов')

    check_and_add_ingredients(model, validated_ingredients)

    return validated_ingredients
