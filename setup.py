#!/usr/bin/env python

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='p2pproxy-record-manager',
    version='0.1',
    description='Application to manage records for Local TS Proxy.',
    long_description=long_description,
    author='Said Babayev',
    author_email='phoenix49@gmail.com',
    license='GPLv3',
    url='https://github.com/ph0enix49/p2pproxy-record-manager',
    packages=['record_manager'],
    install_requires=[
        'beautifulsoup4>=4.4.0',
        'Flask>=0.10.0',
        'Flask-WTF',
        'Jinja2',
        'Werkzeug',
        'WTForms>=2.0',
        'requests>=2.9.0',
    ],
    entry_points={
        'console_scripts': [
            'record_manager=record_manager.record_manager:main',
        ],
    },
)
