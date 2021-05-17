"""
Description

Setup script to install nebulizer: command line utilities for managing
users, tools and data libraries in Galaxy instances via the API

Copyright (C) University of Manchester 2015-2021 Peter Briggs

"""

from setuptools import setup
import codecs
import os.path

# Installation requirements
install_requires = ['bioblend>=0.15.0',
                    'mako',
                    'click==7.1.2',]

# Acquire package version for installation
# (see https://packaging.python.org/guides/single-sourcing-package-version/)
def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

NEBULIZER_VERSION = get_version("nebulizer/__init__.py")

# Get long description from the project README
readme = read('README.rst')

# Setup for installation etc
setup(
    name = "nebulizer",
    version = NEBULIZER_VERSION,
    description = "CLI for remote admin of Galaxy servers",
    long_description = readme,
    url = 'https://github.com/pjbriggs/nebulizer',
    maintainer = 'Peter Briggs',
    maintainer_email = 'peter.briggs@manchester.ac.uk',
    packages = ['nebulizer',],
    entry_points = { 'console_scripts': [
        'nebulizer = nebulizer.cli:nebulizer',]
    },
    license = 'AFL',
    install_requires = install_requires,
    test_suite = 'nose.collector',
    tests_require = ['nose'],
    platforms="Posix; MacOS X; Windows",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Academic Free License (AFL)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "Programming Language :: Python :: 3 :: Only",
    ],
    include_package_data=True,
    zip_safe = False
)
