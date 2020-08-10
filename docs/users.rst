==============
Managing Users
==============

Querying user information
-------------------------

``list_users`` displays user emails and names in a Galaxy
instance:

::

   nebulizer list_users GALAXY

* ``-l``: returns extended information for each user (status,
  whether they are an admin user, disk usage and quota size
  and usage).
* ``--status``: filter list on user status, which can be one of
  ``active`` (the default), ``deleted`` (only list deleted
  users which haven't been purged) or ``all`` (list all active,
  deleted, and purged users).
* ``--name``: filter list on user email (can include glob-style
  wildcards e.g. ``--name="*bloggs*"``).

Creating and deleting individual users
--------------------------------------

``create_user`` makes a new user account:

::

   nebulizer create_user GALAXY USER@DOMAIN [ PUBLIC_NAME ]

If ``PUBLIC_NAME`` is not supplied then one will be
generated automatically from the email address.
   
* ``-c``: check if the account already exists
* ``-p``: supply password for the new account
  (otherwise Nebulizer will prompt for a password)

``delete_user`` removes a user account:

::

   nebulizer delete_user GALAXY USER@DOMAIN

* ``--purge``: purge the account as well as deleting

Creating batches of users from a template name
----------------------------------------------

``create_batch_users`` makes a set of user accounts
based on a template name:

::

   nebulizer create_batch_users GALAXY TEMPLATE [START] END

The template email address should include a ``#`` symbol
which acts as as a placeholder for an integer index, e.g.

::

   user#@example.org

The integer indices are generate from the range
``START...END`` (if ``START`` is not supplied then it is
set to 1).

For example:

::

   nebulizer create_batch_users user#@example.org 1 5

creates accounts:

::

   user1@galaxy.org
   user2@galaxy.org
   user3@galaxy.org
   user4@galaxy.org
   user5@galaxy.org

* ``-c``: check if the accounts already exist
* ``-p``: supply password for the new accounts
  (otherwise Nebulizer will prompt for a password);
  the same password will be applied to all the
  new accounts

Creating user accounts from a file
----------------------------------

``create_users_from_file`` makes a set of user accounts
using data from a file:

::
   
   nebulizer create_users_from_file GALAXY USERS_FILE

``USER_FILE`` is a tab-delimited file with the following
fields on each line:

::

   email|password|public_name

defining a new account.

.. note::

   Optionally ``public_name`` can be left out and will
   then be generated automatically.

* ``-c``: check if the accounts already exist
