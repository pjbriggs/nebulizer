nebulizer
=========

``nebulizer`` is a set of command line utilities to help with managing users,
data libraries and tools in a `Galaxy <https://galaxyproject.org/>`_
instance, using the Galaxy API via the `Bioblend
<http://bioblend.readthedocs.org/en/latest/>`_ Python library.

Installation
------------

It is recommended to install ``nebulizer`` via ``pip`` in a virtualenv, for
example::

  % virtualenv .venv; . .venv/bin/activate
  % pip install git+https://github.com/pjbriggs/nebulizer.git

Setup
-----

Although ``nebulizer``'s commands can be used without addition setup, it is
possible to create shortcuts in the form of 'aliases' to Galaxy URLs and API
key pairs, by creating a ``.nebulizer`` file in your home directory, e.g.::

  % touch ~/.nebulizer

and populating with tab-delimited lines with ``alias|URL|API key``, for
example::

  localhost	http://127.0.0.1:8080	4af252f2250818d14949b3cf0aed476a

Then, rather than specifying the full URL and API key each you can just use
the alias, for example::

  % manage_users list localhost

instead of::

  % manage_users list http://127.0.0.1:8080 -k 4af252f2250818d14949b3cf0aed476a

Commands
--------

Currently ``nebulizer`` offers three utilities:

 * ``manage_users``: list and create user accounts
 * ``manage_libraries``: list, create and populate data libraries
 * ``manage_tools``: list and install tools from toolsheds
