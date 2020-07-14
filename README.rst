.. figure:: https://raw.githubusercontent.com/pjbriggs/nebulizer/master/docs/nebulizer_logo.png
   :alt: Nebulizer Logo
   :align: center
   :figwidth: 100%
   :target: https://github.com/pjbriggs/nebulizer

Command-line utilities to help with managing users, data libraries and
tools in a `Galaxy <https://galaxyproject.org/>`_ instance, using the
Galaxy API via the `Bioblend <http://bioblend.readthedocs.org/en/latest/>`_
library.

.. image:: https://readthedocs.org/projects/pip/badge/?version=latest
   :target: https://nebulizer.readthedocs.io

.. image:: https://badge.fury.io/py/nebulizer.svg
   :target: https://pypi.python.org/pypi/nebulizer/

.. image:: https://travis-ci.org/pjbriggs/nebulizer.png?branch=master
   :target: https://travis-ci.org/pjbriggs/nebulizer

* Free software: Academic Free License version 3.0
* Documentation: https://nebulizer.readthedocs.io
* Code: https://github.com/pjbriggs/nebulizer

.. note::

   **Nebulizer is still a work in progress.**

   Please exercise caution when attempting irreversible operations,
   especially against production Galaxy instances (for example when
   creating users or data libraries).

Quick Start
-----------

This quick start gives some examples of using ``nebulizer`` commands
to perform remote administration tasks on a Galaxy instance from the
command line.

-----------------
Getting Nebulizer
-----------------

It is recommended to install Nebulizer via ``pip`` in a virtualenv,
for example:

::

  % virtualenv .venv
  % sourc .venv/bin/activate
  % pip install nebulizer

This will provide an executable called ``nebulizer`` with a number
of subcommands for performing different tasks remotely on Galaxy
instances.

----------------
Nebulizer Basics
----------------

Generally Nebulizer commands take the form:

::

   nebulizer COMMAND GALAXY [OPTIONS]

To interact remotely with a Galaxy instance using Nebulizer requires
at minimum the URL of the instance and then either an API key or a
user login name.

For example to list the data libraries available on Galaxy Main:

::

  nebulizer -k 9b376af2250818d14949b3c list_libraries https://usegalaxy.org

or

::

  nebulizer -u USER@DOMAIN list_libraries https://usegalaxy.org

In this second case Nebulizer will prompt for the Galaxy
password to authenticate the user login, unless it's supplied via
the ``-P`` option.

To store the Galaxy URL-API key pair against an alias ``main``, to
avoid needing full authentication details each time:

::

  nebulizer add_key main https://usegalaxy.org 9b376af2250818d14949b3c

or alternatively get Nebulizer to fetch the API key itself by
supplying the user login:

::

  nebulizer -u USER@DOMAIN add_key main https://usegalaxy.org

More information on managing API keys in Nebulizer can found
`here <http://nebulizer.readthedocs.io/en/latest/managing_keys.html>`_.

The stored alias is then used in subsequent commands, for example
to list the data libraries again it is now sufficient to do just:

::

  nebulizer list_libraries main

The following sections contain examples of how Nebulizer might be
used to perform various administrive tasks.

Nebulizer provides subcommands to perform various administrive tasks:

`Managing users <http://nebulizer.readthedocs.io/en/latest/users.html>`_:

 * ``list_users``
 * ``create_user``
 * ``create_batch_users``
 * ``create_users_from_file``
 * ``delete_user``

`Managing data libraries <http://nebulizer.readthedocs.io/en/latest/libraries.html>`_:

 * ``list_libraries``
 * ``create_library``
 * ``create_library_folder``
 * ``add_library_datasets``

`Managing tools <http://nebulizer.readthedocs.io/en/latest/tools.html>`_:

 * ``list_tools``
 * ``list_tool_panel``
 * ``list_installed_tools``
 * ``install_tool``
 * ``update_tool``
 * ``uninstall_tool``
 * ``search_toolshed``

`Querying Galaxy instances <http://nebulizer.readthedocs.io/en/latest/querying_galaxy.html>`_:

 * ``ping`` (check if a Galaxy instance is alive)
 * ``config`` (fetch configuration for a Galaxy instance)

See the `tutorial <http://nebulizer.readthedocs.io/en/latest/users.html>`_
for a walkthrough some of these commands.
