#!/usr/bin/python
# -*- coding: utf-8
from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from pathlib import Path
import shutil
import re
import os


try:
    import __builtin__
    input = getattr(__builtin__, 'raw_input')
except (ImportError, AttributeError):
    pass


class FuzzyMatcher():

    def __init__(self):
        self.pattern = ''

    def setPattern(self, pattern):
        self.pattern = '.*?'.join(map(re.escape, list(pattern)))

    def score(self, string):
        match = re.search(self.pattern, string)
        if match is None:
            return 0
        else:
            return 100.0 / ((1 + match.start()) * (match.end() - match.start() + 1))

    def get_string(self, string):
        match = re.search(self.pattern, string)
        if match is None:
            return 0
        else:
            return match.end()


class ConfBase(object):
    command = None
    command_list = ()

    def try_parse(self, command, keyword):
        if not self.command:
            raise NotImplementedError()
        fm = FuzzyMatcher()
        fm.setPattern(command)
        return fm.score(keyword)

    def parse_command(self, command):
        if not command:
            return
        command_split = command.split(' ')
        command_matched = sorted([(self.try_parse(command_split[0], x), y, x) for x, y in self.command_list], key=lambda x: x[0], reverse=True)[0]
        if command_matched[0]:
            if isinstance(command_matched[1], str):
                if not command_split[1:]:
                    getattr(self, command_matched[1])()
                else:
                    getattr(self, command_matched[1])(command_split[1:])
            elif isinstance(command_matched[1], ConfBase):
                if not command_split[1:]:
                    command_matched[1].run()
                else:
                    command_matched[1].run(command_split[1:])
            else:
                raise TypeError('Not know type %s' % type(command_matched[1]))
        else:
            print('command not found.')


class ConfApp(ConfBase):
    '''
    Configure INSTALLED_APPS
    '''
    command = 'app'
    command_list = (('show', 'show'), ('add', 'add'), ('delete', 'delete'), ('clear', 'clear'), ('exit', 'exit'), ('save', 'save'))
    current_apps = []

    def __init__(self, conf_main):
        self.conf_main = conf_main
        start_matching = 'INSTALLED_APPS += +\('
        end_matching = '\)'
        listing_app = False
        self.current_apps = []
        for line in self.conf_main.conf_datas:
            if re.match(start_matching, line):  # found
                listing_app = True
            if listing_app:
                if re.match(end_matching, line):
                    listing_app = False
                else:
                    result = re.search("'(?P<app_name>[a-zA-Z0-9.]+)',{0,1}", line)
                    if result:
                        self.current_apps.append(result.group('app_name'))
        self.is_exit = False

    def show(self):
        print('Installed Applications:')
        for app in self.current_apps:
            print(app)

    def add(self, argv):
        app_name = argv[0]
        self.current_apps.append(app_name)

    def delete(self, argv):
        app_name = argv[0]
        self.current_apps.remove(app_name)

    def compile_command_list(self):
        self.new_command_list = []
        for x, y in self.command_list:
            if '$app' in x:
                for app in self.current_apps:
                    self.new_command_list.append((x, y))
            else:
                self.new_command_list.append((x, y))

    def run(self):
        self.is_exit = False
        while not self.is_exit:
            command = input('app#')
            self.parse_command(command)

    def exit(self):
        self.save()
        self.is_exit = True

    def save(self):
        print('Saving change...')
        start_matching = 'INSTALLED_APPS += +\('
        end_matching = '\)'
        listing_app = False
        new_conf_datas = []
        for line in self.conf_main.conf_datas:
            if re.match(start_matching, line):  # found
                listing_app = True
                new_conf_datas.append(line)
                for app_name in self.current_apps:
                    new_conf_datas.append("    '%s',\n" % app_name)
                continue
            if listing_app:
                if re.match(end_matching, line):
                    listing_app = False
                    new_conf_datas.append(line)
            else:
                new_conf_datas.append(line)
        self.conf_main.conf_datas = new_conf_datas


class ConfMain(ConfBase):
    command = 'main'
    command_list = [('show', 'show'), ('exit', 'exit'), ('save', 'save'), ('timezone', 'timezone'), ('autoconfig', 'autoconfig'), ('initialize', 'initialize'), ('help', 'help')]

    def __init__(self, package_path=Path('.')):
        print('Django Configure 1.0')
        print('Type "help" for more information.')
        setting_path      = os.environ.get("DJANGO_SETTINGS_MODULE")  # 'projectname.settings'
        self.project_name = setting_path.split('.')[0]
        setting_path      = './' + setting_path.replace('.', '/') + '.py'
        self.project_path = Path(self.project_name)
        self.root_path    = self.project_path.parent
        self.setting_path = Path(setting_path)
        self.package_path = package_path
        self.files_path   = package_path / 'files'
        self.load()

        conf_list = []
        conf_list.append(ConfApp(self))
        self.command_list += [(conf_app.command, conf_app) for conf_app in conf_list]

    def load(self):
        '''
        Load setting from settings.py
        '''
        print('Load settings.')
        with self.setting_path.open('r') as f:
            self.conf_datas = f.readlines()

    def autoconfig(self):
        '''
        Auto configuration such as STATICFILES_DIRS, STATIC_ROOT,
              TEMPLATE_DIRS, MEDIA_ROOT, MEDIA_URL
        '''
        autoconfig_gen = (
            ("STATICFILES_DIRS", "[os.path.join(BASE_DIR, 'static')]"),
            ("STATIC_ROOT", "os.path.join(BASE_DIR, 'static_root')"),
            ("TEMPLATE_DIRS", "[os.path.join(BASE_DIR, 'templates')]"),
            ("MEDIA_ROOT", "os.path.join(BASE_DIR, 'media')"),
            ("MEDIA_URL", "'/media/'"),
        )
        for key, val in autoconfig_gen:
            print('Checking %s' % (key))
            target_val = None
            for line in self.conf_datas:
                result = re.match(r"%s += +(?P<target_val>.+)" % (key.replace('_', '\\_')), line)
                if result:
                    target_val = result.group('target_val')
            if target_val:
                print(' ... Found, skipped')
            else:
                print(' ... Not Found, include')
                self.conf_datas.append("%s = %s\n" % (key, val))
        print('End auto config.')

    def show(self):
        '''
        Show settings
        '''
        print(''.join(self.conf_datas))

    def run(self):
        self.is_exit = False
        while not self.is_exit:
            command = input('>')
            self.parse_command(command)

    def timezone(self):
        '''
        Set Timezone
        '''
        now_timezone = None
        for line in self.conf_datas:
            result = re.match(r"TIME\_ZONE += +'(?P<now_timezone>.+)'", line)
            if result:
                now_timezone = result.group('now_timezone')

        change_timezone = input('TimeZone (%s):' % now_timezone)
        if not change_timezone:
            print('Nothing changed.')
            return
        else:
            for count in range(len(self.conf_datas)):
                line = self.conf_datas[count]
                result = re.match(r"TIME\_ZONE += +'(?P<now_timezone>.+)'", line)
                if result:
                    self.conf_datas[count] = "TIME_ZONE = '%s'\n" % change_timezone
                    print('Timezone changed.')
                    return
            self.conf_datas.append("TIME_ZONE = '%s'\n" % change_timezone)
            print('Save new timezone.')

    def help(self):
        '''
        Show this help menu
        '''
        for command in self.command_list:
            if isinstance(command[1], str):
                doc = getattr(self, command[1]).__doc__.strip()
                print('%-12s: %s' % (command[0], doc))
            elif isinstance(command[1], ConfBase):
                doc = command[1].__doc__.strip()
                print('%-12s: %s' % (command[0], doc))

    def initialize(self):
        '''
        Initialize template with settings and utils files.
        '''
        print('Re-initial configuration (Old settings will be lost).')
        print('copying common_settings.py')
        files_common_settings_path = self.files_path / 'common_settings.py'
        with files_common_settings_path.open('r') as fr:
            new_data = fr.read().replace('{DJANGO_PROJECT}', self.project_name)

            chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
            new_data = new_data.replace('{SECRET_KEY}', get_random_string(50, chars))

            common_settings = self.project_path / 'common_settings.py'
            with common_settings.open('w') as fw:
                fw.write(new_data)
        print('copying %s' % (self.project_path / 'settings.py'))

        shutil.copy(str(self.files_path / 'settings.py'), str(self.project_path / 'settings.py'))
        print('copying secrets.json.default')
        shutil.copy(str(self.files_path / 'secrets.json.default'), str(self.root_path / 'secrets.json.default'))
        if not os.path.exists('utils'):
            print('creating utils')
            os.makedirs('utils')
        print('copying utils/__init__.py')
        shutil.copy(str(self.files_path / 'utils' / '__init__.py'), str(self.root_path / 'utils' / '__init__.py'))
        print('copying utils/decorators.py')
        shutil.copy(str(self.files_path / 'utils' / 'decorators.py'), str(self.root_path / 'utils' / 'decorators.py'))
        print('copying utils/misc.py')
        shutil.copy(str(self.files_path / 'utils' / 'misc.py'), str(self.root_path / 'utils' / 'misc.py'))
        print('copying fabfile.py')
        shutil.copy(str(self.files_path / 'fabfile.py'), str(self.root_path / 'fabfile.py'))
        self.load()

    def exit(self):
        '''
        Save and exit.
        '''
        self.save()
        self.is_exit = True

    def save(self):
        '''
        Save changed settings
        '''
        print('Saving change to setings.')
        with self.setting_path.open('w') as f:
            f.write(''.join(self.conf_datas))


class Command(BaseCommand):
    help = ''
    state = ''

    def handle(self, *args, **options):
        package_path = Path(__file__).parent.parent.parent
        ConfMain(package_path=package_path).run()
        self.stdout.write('Bye.')
