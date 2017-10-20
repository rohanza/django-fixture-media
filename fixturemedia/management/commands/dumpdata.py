import os
from os.path import abspath, dirname, exists, join
from django.core.management.commands import dumpdata
from django.core.management import CommandError
from django.core.serializers import get_serializer
from django.db.models.fields.files import FileField
from django.core.files.storage import default_storage
from django.core.files.base import File
from fixturemedia.util import models_with_filefields, pre_dump, get_dump_object


class Command(dumpdata.Command):
    def save_images_for_signal(self, sender, **kwargs):
        instance = kwargs['instance']
        for field in sender._meta.fields:
            if not isinstance(field, FileField):
                continue
            path = getattr(instance, field.attname)
            if path is None or not path.name:
                continue

            if not default_storage.exists(path.name):
                continue

            target_path = join(self.target_dir, path.name)
            if not exists(dirname(target_path)):
                os.makedirs(dirname(target_path))

            in_file = default_storage.open(path.name, 'rb')
            file_contents = in_file.read()
            in_file.close()

            with open(target_path, 'wb') as out_file:
                out_file.write(file_contents)

    def set_up_serializer(self, ser_format):
        try:
            super_serializer = get_serializer(ser_format)
        except KeyError:
            raise CommandError("Unknown serialization format: {}".format(ser_format))

        # patch the base serializer to send our `pre_dump` signal
        super_serializer.get_dump_object = get_dump_object

    def handle(self, *app_labels, **options):
        ser_format = options.get('format')
        outfilename = options.get('output')

        if outfilename is None:
            raise CommandError('No --outfile specified (this is a required option)')
        self.target_dir = join(dirname(abspath(outfilename)), 'media')

        for modelclass in models_with_filefields():
            pre_dump.connect(self.save_images_for_signal, sender=modelclass)

        self.set_up_serializer(ser_format)

        with File(open(outfilename, 'w')) as self.stdout:
            super(Command, self).handle(*app_labels, **options)
