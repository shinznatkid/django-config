from fabric.api import local


def upload():
    # local('python setup.py bdist_wheel upload')
    local('rm -r ./dist')
    local('python setup.py sdist bdist_wheel')
    local('twine upload --repository-url https://upload.pypi.org/legacy/ dist/*')
