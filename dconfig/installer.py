# -*- coding: utf-8

import os
import shutil
import importlib
from pathlib import Path
from collections import OrderedDict


class RequirementEditor:

    def __init__(self, requirements_data):
        lines = []
        for line in requirements_data.split('\n'):
            line = line.strip()
            if line:
                lines.append(line)
        self.requirements_dict = OrderedDict()
        for item in lines:
            item_datas = item.split('==', 2)
            name = item_datas[0]
            version = None
            if len(item_datas) == 2:
                version = item_datas[1]
            self.requirements_dict[name] = version

    def exists(self, app_name):
        return app_name in self.requirements_dict

    def add(self, app_name, version=None):
        self.requirements_dict[app_name] = version

    def serialize(self):
        return_string = ''
        for app_name, version in self.requirements_dict.items():
            if version:
                return_string += '{}=={}\n'.format(app_name, version)
            else:
                return_string += '{}\n'.format(app_name)
        return return_string


class AppInstaller:

    AVAILABLE_APPS = ['sentry_sdk', 'picker', 'sass_processor', 'rest_framework']
    RECOMMEND_APPS = ['sentry_sdk', 'picker']

    def __init__(self, package_path):
        self.package_path = package_path
        self.files_path   = package_path / 'files'
        setting_path      = os.environ.get("DJANGO_SETTINGS_MODULE")  # 'projectname.settings'
        self.project_name = setting_path.split('.')[0]
        self.project_path = Path(self.project_name)
        self.root_path    = self.project_path.parent

    def get_settings_dconfig_version(self):
        '''
        if visible
            return (major, minor)
        Otherwise
            return None
        '''
        common_setting_path = self.project_path / 'common_settings.py'
        if not common_setting_path.exists():
            return

        with open(str(common_setting_path)) as fr:
            for line in fr.readlines():
                if line.startswith('# dconfig: '):  # matched
                    raw_version = line[len('# dconfig: '):]
                    major_version, minor_version = raw_version.strip().split('.')  # e.g. 1.1
                    return int(major_version), int(minor_version)

    def get_install_app_name(self, app_name):
        app_name = app_name.lower()
        if app_name in self.AVAILABLE_APPS:
            return app_name
        # TODO: Suggestion related keyword?
        return False

    def edit_install_code(self, app_name):
        '''
        แก้ไขที่
        1. __init__.py ใน auto_setting_modules
        2. auto_settings.py
        '''

        # auto_settings.py
        AUTO_SETTINGS_HEADERS = 'from .auto_setting_modules import *'
        auto_settings_datas = [AUTO_SETTINGS_HEADERS]

        print('editing {}/auto_settings.py'.format(self.project_name))
        auto_settings = importlib.import_module('{}.auto_settings'.format(self.project_name))
        values = auto_settings.AUTO_INSTALLED_APPS
        if not isinstance(values, list):
            values = []  # Override
        if app_name not in values:
            values.append(app_name)
        auto_settings_datas.append('AUTO_INSTALLED_APPS = {}'.format(values))

        auto_setting_path = self.project_path / 'auto_settings.py'
        with auto_setting_path.open('wt') as file_write:
            file_write.write('\n'.join(auto_settings_datas))
            file_write.write('\n')

    def edit_requirements(self, requirements):
        # Insert to requirements.txt
        requirements_version = 1
        requirements_path = self.root_path / 'requirements.txt'
        requirements_version_2_path = self.root_path / 'requirements' / 'base.txt'
        if os.path.exists(str(requirements_path)):
            with requirements_path.open('rt') as f:
                old_req_data = f.read()
            if old_req_data.startswith('-r requirements/base.txt'):  # New system detected!
                requirements_version = 2
        if os.path.exists(str(requirements_version_2_path)):
            requirements_version = 2

        if requirements_version == 2:
            if not os.path.exists(str(self.root_path / 'requirements')):
                print('creating {}'.format('requirements'))
                os.makedirs(str('requirements'))
            requirements_path = requirements_version_2_path
            print('editing requirements/base.txt')
        else:
            print('editing requirements.txt')

        if os.path.exists(str(requirements_path)):
            with requirements_path.open('rt') as f:
                old_req_data = f.read()
        else:
            old_req_data = ''
        requirement_editor = RequirementEditor(old_req_data)
        for requirement_item in requirements:
            requirement_editor.add(requirement_item)
        requirement_data = requirement_editor.serialize()
        with requirements_path.open('wt') as f:
            f.write(requirement_data)

    def install_app(self, raw_app_name):

        app_name = self.get_install_app_name(raw_app_name)
        if not app_name:
            print('App "{}" not found.'.format(raw_app_name))
            return False

        app_package = importlib.import_module('dconfig.files.auto_setting_modules.{}.package'.format(app_name))
        print('files = {}'.format(app_package.files))
        print('requirements = {}'.format(app_package.requirements))

        folder_path = str(self.project_path / 'auto_setting_modules' / app_name)
        if not os.path.exists(folder_path):
            print('creating {}'.format(folder_path))
            os.makedirs(folder_path)

        for file_name in app_package.files:
            print('copying {}'.format(file_name))
            source_path = self.files_path / 'auto_setting_modules' / app_name / file_name
            dest_path = self.project_path / 'auto_setting_modules' / app_name / file_name
            # shutil.copy(str(source_path), str(dest_path))
            with source_path.open('r') as fr:
                new_data = fr.read().replace('{DJANGO_PROJECT}', self.project_name)
                with dest_path.open('w') as fw:
                    fw.write(new_data)

        self.edit_requirements(app_package.requirements)
        self.edit_install_code(app_name)

        print('{} installed.'.format(app_name))
        return True
