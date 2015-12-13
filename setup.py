#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
from setuptools import setup

pkg_name = 'samtt'

classifiers = [
    "Development Status :: 3 - Alpha",
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Topic :: Database',
]

#tests = [
#    'samtt.tests',
#]

descr = 'Multithread transaction tracker for sqlalchemy'
with open(os.path.join(pkg_name, '__init__.py')) as f:
    long_description = f.read().split('"""')[1]

setup_kwargs = dict(
    name=pkg_name,
    version="0.1",
    description=descr,
    long_description=long_description,
    classifiers=classifiers,
    author='Johan Egneblad',
    author_email='johan.egneblad@DELETEMEgmail.com',
    url='https://github.com/eblade/sqlalchemy-mtt',
    license='BSD',
    packages=[pkg_name], # + tests,
    extras_require={'all': ['sqlalchemy']}
)

if __name__ == '__main__':
    setup(**setup_kwargs)
