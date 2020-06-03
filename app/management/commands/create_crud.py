from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from restframework_core.gen_code import CodeGenerator


class Command(BaseCommand):
    help = "create crud code according ModelViewSet"

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
        gen = CodeGenerator()

        create_configs = []
        for config in configs:
            if config.name in exclude_apps:
                pass
            else:
                gen.init_files(config.path)
                create_configs.append(config)
        
        gen.write_file_header(create_configs)
        self.stdout.write("file header finish")
        gen.batch_gen_code(create_configs)

        self.stdout.write("success")
