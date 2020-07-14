=============
Configuration
=============

Nebulizer doesn't require any additional configuration after
installation: it is possible to supply either a Galaxy API key
or a Galaxy username/password combination on the command line
(alongside the URL of the Galaxy instance) each time a command
is executed.

However this is both laborious and potentially insecure.
Nebulizer can store Galaxy URL-API key pairs against aliases
locally to make this easier, using the ``add_key`` command.

The simplest way to create a new alias is:

::

   nebulizer -u EMAIL add_key ALIAS GALAXY_URL

Nebulizer will prompt for the password for the account and
will then fetch and store the API key automatically.

.. note::

   For example: to add an alias ``main`` for Galaxy main at
   https://usegalaxy:

   ::

      nebulizer -u peter.briggs@manchester.ac.uk add_key main https://usegalaxy.org

Alternatively you can supply an API directly on the command
line:

::

   nebulizer add_key ALIAS GALAXY_URL API_KEY

.. note::

   For example:

   ::

      nebulizer add_key main https://usegalaxy.org 9b376af2250818d14949b3c

The stored alias can then be used instead of supplying the
full Galaxy URL with an email/password combination or an
API key; for example to get configuration information from
Galaxy main using the ``config`` command:

::

  nebulizer config main

See :doc:`managing_keys` for more information on managing stored
aliases.
