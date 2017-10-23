from os.path import dirname, isdir, join

from django.apps import apps
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.management.commands import loaddata
from django.db.models import signals
from django.db.models.fields.files import FileField
from django.utils._os import upath
from fixturemedia.util import models_with_filefields


class Command(loaddata.Command):
    def load_images_for_signal(self, sender, **kwargs):
        instance = kwargs['instance']
        for field in sender._meta.fields:
            if not isinstance(field, FileField):
                continue
            path = getattr(instance, field.attname)
            if path is None or not path.name:
                continue
            for fixture_path in self.fixture_media_paths:
                filepath = join(fixture_path, path.name)
                try:
                    with open(filepath, 'rb') as f:
                        default_storage.save(path.name, f)
                except IOError:
                    self.stderr.write("Expected file at {} doesn't exist, skipping".format(filepath))
                    continue

    def handle(self, *fixture_labels, **options):
        # Hook up pre_save events for all the apps' models that have FileFields.
        for modelclass in models_with_filefields():
            signals.pre_save.connect(self.load_images_for_signal, sender=modelclass)

        fixture_paths = self.find_fixture_paths()
        fixture_paths = (join(path, 'media') for path in fixture_paths)
        fixture_paths = [path for path in fixture_paths if isdir(path)]
        self.fixture_media_paths = fixture_paths

        return super(Command, self).handle(*fixture_labels, **options)

    def find_fixture_paths(self):
        """Return the full paths to all possible fixture directories."""
        app_module_paths = []
        app_configs = apps.get_app_configs()
        app_models_modules = [ac.models_module for ac in app_configs if ac.models_module is not None]
        for app in app_models_modules:
            if hasattr(app, '__path__'):
                # It's a 'models/' subpackage
                for path in app.__path__:
                    app_module_paths.append(upath(path))
            else:
                # It's a models.py module
                app_module_paths.append(upath(app.__file__))

        app_fixtures = [join(dirname(path), 'fixtures') for path in app_module_paths]

        return app_fixtures + list(settings.FIXTURE_DIRS)
