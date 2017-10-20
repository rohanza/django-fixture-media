from django.apps import apps
from django.core.serializers.python import Serializer
from django.db.models import FileField
from django.dispatch import Signal


pre_dump = Signal(providing_args=('instance',))


def models_with_filefields():
    for modelclass in apps.get_models():
        if any(isinstance(field, FileField) for field in modelclass._meta.fields):
            yield modelclass


def get_dump_object(self, obj):
    """
    Serializer patch method to get access to model instance.
    Triggers instance media dump by sending the `pre_dump` signal.
    """
    pre_dump.send(sender=type(obj), instance=obj)
    return Serializer.get_dump_object(self, obj)
