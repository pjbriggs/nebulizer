====================================
Storing and managing Galaxy API keys
====================================

The majority of Nebulizer's commands require valid credentials in
order to interact with a Galaxy instance. These can be supplied
explicitly on the command line each time:

::

   nebulizer -u USER@DOMAIN [ -P PASSWORD ] ...command...
   nebulizer -k API_KEY ...command...

Alternatively it is possible to store Galaxy URL-API key pairs in
a file called ``.nebulizer`` located in the user's home directory,
with each pair being associated with an alias.

The file is created automatically the first time an alias is
created using ``add_key`` command, and consists of tab-delimited
lines with three fields:

::

  alias|Galaxy_URL|API_key

for example:

::

   demo   http://127.0.0.1:8080   4551fbf7cd8b1bc59db....


This file can be manually edited using a text editor such as
``vi``; however Nebulizer also provides a set of commands for
querying and modifying the file contents.

``list_keys`` shows the aliases with their associated Galaxy
URLs:

::

  nebulizer list_keys

.. note::

   By default the API keys are not shown by ``list_keys``;
   use the ``--show-api-keys`` option to include them.

.. note::
   
   Use the ``whomai`` command to find out which user is
   associated with an alias:

   ::

      nebulizer whoami ALIAS

``add_key`` will store a Galaxy-API key combination under a
new alias. If the API key is known then the general form of
the command is:

::

   nebulizer add_key ALIAS GALAXY_URL API_KEY

However it is usually easier to get Nebulizer to fetch the
key automatically, by supplying a Galaxy username (email):

::

   nebulizer -u USER@DOMAIN add_key ALIAS GALAXY_URL

Multiple Galaxy URL-key pairs can be stored; only the
associated aliases need to be unique.

``update_key`` will update the details stored for an existing
alias:

::

   nebulizer update_key ALIAS --new-url GALAXY_URL
   nebulizer update_key ALIAS --new-api-key API_KEY
   nebulizer -u USER@DOMAIN update_key ALIAS --fetch-api-key

``remove_key`` deletes an existing ALIAS and associated
credentials:

::

  nebulizer remove_key ALIAS
