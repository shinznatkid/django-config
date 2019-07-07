from fabric.api import local


def upload():
    # local('python setup.py bdist_wheel upload')
    try:
        local('rm -r ./dist')
    except:
        pass
    local('python setup.py sdist bdist_wheel')
    local('twine upload dist/*')  # optional args --repository-url https://upload.pypi.org/legacy/ or --repository your-repo-name
