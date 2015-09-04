"""
Description

Setup script to install nebulizer: command line utilities for managing
users, tools and data libraries in Galaxy instances via the API

Copyright (C) University of Manchester 2015 Peter Briggs

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
        'manage_users = nebulizer.cli:manage_users',
        'manage_libraries = nebulizer.cli:manage_libraries',
        'manage_tools = nebulizer.cli:manage_tools',]
    },
    license = 'Artistic License',
    install_requires = ['bioblend',
                        'mako'],
    test_suite = 'nose.collector',
    tests_require = ['nose'],
    include_package_data=True,
    zip_safe = False
)
