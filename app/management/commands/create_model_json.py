from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from restframework_core.gen_code import JsonGenerator


class Command(BaseCommand):
    help = "create model json"

    def handle(self, *args, **options):
        exclude_apps = [
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.messages",
            "django.contrib.staticfiles",
            "rest_framework",
            "django_filters",
        ]
        configs = apps.get_app_configs()
        gen = JsonGenerator()

        create_configs = []
        for config in configs:
            if config.name in exclude_apps:
                pass
            else:
                create_configs.append(config)

        gen.batch_gen_json(create_configs)
