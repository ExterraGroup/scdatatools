#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    "pyrsi==0.1.11",
    "pycryptodome==3.9.4",
    "zstandard==0.12.0",
    "python-nubia==0.2b2",
    "ipython==7.14.0"
]

setup_requirements = [
    "setuptools-scm==3.5.0",
    "sphinx==3.0.3"
]

test_requirements = []


if len(sys.argv) >= 2 and sys.argv[1] == 'docs':
    import shutil
    from sphinx.ext import apidoc
    from subprocess import call

    print("Auto-generating API docs")

    proj_dir = os.path.dirname(os.path.realpath(__file__))
    api_dir = os.path.join(proj_dir, 'docs', 'api')
    shutil.rmtree(api_dir, ignore_errors=True)

    _orig_sysargv = sys.argv
    if len(sys.argv) > 2:
        args = sys.argv[2:]
    else:
        args = ['-e', '-M']

    args += ['-o', os.path.join(proj_dir, 'docs', 'api'), os.path.join(proj_dir, 'scdatatools')]
    print(args)
    apidoc.main(args)

    print("Generated API docs - run `python setup.py build_sphinx` to build docs")

    sys.exit(0)



setup(
    author="Ventorvar",
    author_email='ventorvar@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
    description="Python tools for working with Star Citizen data files.",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='scdatatools',
    name='scdatatools',
    packages=find_packages(include=['scdatatools']),
    entry_points={
        'console_scripts': ['scdt=scdatatools.cli:main'],
    },
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/ExterraGroup/scdatatools',
    version='0.1.2',
    zip_safe=True,
)
