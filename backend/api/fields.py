import base64

from django.core.files.base import ContentFile
from rest_framework.fields import ImageField


class Base64ImageField(ImageField):
    """Custom field type for images."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            image_format, imgstr = data.split(';base64,')
            ext = image_format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)
