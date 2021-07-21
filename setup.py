# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

REQUIREMENTS = [
    'requests',
    'requests-oauthlib',
    'requests-toolbelt',
    'xmltodict'
]

# https://pypi.python.org/pypi?%3Aaction=list_classifiers
CLASSIFIERS = []

setup(
    name='erclient',
    version=0.53,
    description='Client for Erecruit API 2.0 with Fallback to 1.0',
    author='siteshell.net',
    author_email='pdbethke@siteshell.net',
    url='https://github.com/pdbethke/erclient',
    packages=find_packages(),
    license='LICENSE.txt',
    platforms=['OS Independent'],
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS,
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),
    include_package_data=True,
    zip_safe=False,
    # test_suite="test_settings.run",
)
