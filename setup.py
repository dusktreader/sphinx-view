import glob
import json

from setuptools import setup, find_packages

with open('.project_metadata.json') as meta_file:
    project_metadata = json.loads(meta_file.read())


setup(
    name=project_metadata['name'],
    version=project_metadata['version'],
    author=project_metadata['author'],
    author_email=project_metadata['author_email'],
    description=project_metadata['description'],
    license=project_metadata['license'],
    install_requires=[
        'Flask',
        'inflection',
        'sphinx',
    ],
    extras_require={
        'dev': [
            'flake8',
            'pytest',
            'pytest-catchlog',
            'pytest-flask',
        ],
    },
    include_package_data=True,
    packages=find_packages(),
    scripts=glob.glob('bin/*'),
)
