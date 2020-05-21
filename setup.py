#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    "pycryptodome==3.9.4",
    "zstandard==0.12.0",
    "python-nubia==0.2b2",
    "ipython==7.14.0"
]

setup_requirements = [
    "setuptools-scm==3.5.0"
]

test_requirements = [ ]

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
    entry_points = {
        'console_scripts': ['scdt=scdatatools.cli:main'],
    },
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/ExterraGroup/scdatatools',
    version='0.1.2',
    zip_safe=True,
)
