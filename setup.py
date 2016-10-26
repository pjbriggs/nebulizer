"""
Description

Setup script to install nebulizer: command line utilities for managing
users, tools and data libraries in Galaxy instances via the API

Copyright (C) University of Manchester 2015-2016 Peter Briggs

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
        'nebulizer = nebulizer.cli:nebulizer',
        'manage_users = nebulizer.deprecated_cli:manage_users',
        'manage_libraries = nebulizer.deprecated_cli:manage_libraries',
        'manage_tools = nebulizer.deprecated_cli:manage_tools',]
    },
    license = 'AFL',
    install_requires = ['bioblend',
                        'mako',
                        'click'],
    test_suite = 'nose.collector',
    tests_require = ['nose'],
    platforms="Posix; MacOS X; Windows",
    classifiers=["Development Status :: 4 - Beta",
                 "Environment :: Console",
                 "Intended Audience :: End Users/Desktop",
                 "Intended Audience :: System Administrators",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: Academic Free License (AFL)",
                 "Operating System :: OS Independent",
                 "Topic :: Scientific/Engineering",
                 "Topic :: Scientific/Engineering :: Bio-Informatics",
                 "Programming Language :: Python :: 2",
                 "Programming Language :: Python :: 2.7"],
    include_package_data=True,
    zip_safe = False
)
