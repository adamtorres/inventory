from rest_framework import serializers


class CharField(serializers.CharField):
    def __init__(self, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 1024)
        kwargs['allow_blank'] = kwargs.get('allow_blank', True)
        kwargs['allow_null'] = kwargs.get('allow_null', False)
        kwargs['default'] = kwargs.get('default', "")
        super().__init__(**kwargs)
