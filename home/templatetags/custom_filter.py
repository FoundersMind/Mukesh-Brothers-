import base64
from django import template
from django.core.files.base import ContentFile
import json

from django.templatetags.static import static

register = template.Library()


@register.filter
def image64(image):
    if hasattr(image, 'path'):  # Check if image is a file object
        with open(image.path, "rb") as f:
            encoded_string = base64.b64encode(f.read())
    else:  # Assume image is already in base64 format
        encoded_string = image.encode('utf-8')
    return encoded_string.decode('utf-8')



@register.filter
def read_json(file_path):
    try:
        with open(static(file_path), 'r') as file:
            data = json.load(file)
        return data
    except Exception as e:
        return {}