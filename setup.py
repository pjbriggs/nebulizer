"""
Description

Setup script to install nebulizer: command line utilities for managing
users, tools and data libraries in Galaxy instances via the API

Copyright (C) University of Manchester 2015-2020 Peter Briggs

"""

readme = open('README.rst').read()

# Setup for installation etc
from setuptools import setup
import nebulizer
setup(
    name = "nebulizer",
    version = nebulizer.get_version(),
    description = "Manage users, tools and libraries in Galaxy",
    long_description = readme,
    url = 'https://github.com/pjbriggs/nebulizer',
    maintainer = 'Peter Briggs',
    maintainer_email = 'peter.briggs@manchester.ac.uk',
    packages = ['nebulizer',],
    entry_points = { 'console_scripts': [
        'nebulizer = nebulizer.cli:nebulizer',]
    },
    license = 'AFL',
    install_requires = ['bioblend>=0.13.0',
                        'mako',
                        'click<=6.7'],
    test_suite = 'nose.collector',
    tests_require = ['nose'],
    platforms="Posix; MacOS X; Windows",
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
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    include_package_data=True,
    zip_safe = False
)
