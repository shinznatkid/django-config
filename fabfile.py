from fabric.api import local


def upload():
    local('python setup.py bdist_wheel upload')
