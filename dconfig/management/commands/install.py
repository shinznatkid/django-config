# -*- coding: utf-8

from pathlib import Path

from django.core.management.base import BaseCommand
from ...installer import AppInstaller


class Command(BaseCommand):
    help = ''
    state = ''

    def add_arguments(self, parser):
        parser.add_argument(
            'app_name',
            nargs='*',
            type=str,
            help='Install "app_name" to project'
        )

    def handle(self, *args, **options):

        package_path = Path(__file__).parent.parent.parent
        installer = AppInstaller(package_path)

        if not options['app_name']:
            print('How to use: "python manage.py install APP_NAME"')
            print('Availables Apps: {}'.format(', '.join(AppInstaller.AVAILABLE_APPS)))
        else:
            for app_name in options['app_name']:
                installer.install_app(app_name)
