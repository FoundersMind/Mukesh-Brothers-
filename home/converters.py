from django.urls.converters import StringConverter

class FloatConverter(StringConverter):
    regex = '[-+]?[0-9]*\.?[0-9]+'
