#!/usr/bin/env python3

from setuptools import setup
with open('VERSION', 'r') as fn:
    VERSION = fn.read().split('\n')[0]

setup(name='apilassian',
      version=VERSION,
      description='Atlassian API implementation',
      url='https://github.com/devopsysadmin/apilassian.git',
      license='GPLv2',
      packages=['apilassian', 'atcli'],
      zip_safe=False,
      install_requires=[line for line in open('requirements.txt')],
      entry_points={
        'console_scripts': [
            'atcli = atcli.py:main'
            ],
        },
      )
