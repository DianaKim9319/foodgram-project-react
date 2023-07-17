from rest_framework import status
from rest_framework.response import Response


class IngredienteMixin:
    @staticmethod
    def ing_create_update(item, model, instance):
        ingredients_obj = []
        for ingredient in item:
            amount = ingredient['amount']
            ingredient_id = ingredient['id']
            ingredients_obj.append(model(
                recipe=instance,
                ingredient_name=ingredient_id,
                amount=amount
            ))

        model.objects.bulk_create(ingredients_obj)


class IsSubscribedMixin:
    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.following.filter(user=request.user).exists()
        return False


class AddDeleteMixin:
    @staticmethod
    def add_delete(
            request,
            item,
            field_name,
            model,
            serializer_class,
            error_message,
            success_message
    ):
        if request.method == 'POST':
            _, created = model.objects.get_or_create(
                user=request.user,
                **{field_name: item}
            )
            if created:
                serializer = serializer_class(
                    item,
                    context={'request': request}
                )
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'error': [error_message['post']]},
                status=status.HTTP_400_BAD_REQUEST
            )

        model_obj = model.objects.filter(
            user=request.user,
            **{field_name: item}
        )
        if model_obj.exists():
            model_obj.delete()
            response_data = {'message': success_message}
            return Response(
                response_data,
                status=status.HTTP_200_OK
            )

        return Response(
            {'error': [error_message['delete']]},
            status=status.HTTP_400_BAD_REQUEST
        )
