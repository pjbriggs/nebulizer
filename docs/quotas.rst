===============
Managing Quotas
===============

Querying quotas
---------------

``quotas`` lists the quotas defined in a Galaxy instance:

::

   nebulizer quotas GALAXY

* ``-l``: returns extended information for each quota, including
  the associated users and groups.
* ``--status``: filter list on quota status, which can be one of
  ``active`` (the default), ``deleted`` (only list deleted
  quotas) or ``all`` (list all active and deleted quotas).
* ``--name``: filter list on quota name (can include glob-style
  wildcards e.g. ``--name="*NGS*"``).

Creating and deleting quotas
----------------------------

``quotaadd`` defines a new quota:

::

   nebulizer quotaadd GALAXY QUOTA_NAME SIZE

``SIZE`` can either be an amount (e.g. ``10GB``, ``0.2 T``) or
an amount preceeded by an operation (one of ``+``, ``-`` or
``=``, e.g. ``=300gb``, ``+100G``). If an operation isn't
specified then ``=`` is assumed.

* ``-d``/``--description``: set the description for the quota
  (defaults to the quota name).
* ``--default_for``: set the quota as the the default for either
  'registered' or 'unregistered' users.

Users and groups can be associated with the new quota using the
``-u`` and ``-g`` options:

* ``-u``/``--users``: associate one or more users with the
  quota, as a comma-separated list of email addresses.
* ``-g``/``--groups``: associate one or more groups with the
  quota, as a comma-separated list of group names.

``quotadel`` deletes an existing quota:

::

   nebulizer quotadel GALAXY QUOTA_NAME

.. note::

   A deleted quota can be restored using the ``--undelete``
   option of the ``quotamod`` command.

Modifying quota definitions
---------------------------

``quotamod`` updates a quota definition:

::

   nebulizer quotamod GALAXY QUOTA_NAME ...

Options allow various quota properties to be modified:

* ``-n``/``--name``: sets a new name for the quota.
* ``-d``/``--description``: sets a new description.
* ``-q``/``--quota-size``: updates the size of the quota, and how
  it is applied.
* ``--default_for``: set the quota as the the default for either
  'registered' or 'unregistered' users.

Users and groups can be associated with the following options:

* ``-a``/``--add-users``: associate one or more users with the
  quota, as a comma-separated list of email addresses.
* ``-r``/``--remove-users``: disassociate one or more users from
  the quota, as a comma-separated list of email addresses.
* ``-A``/``--add-groups``: associate one or more groups with the
  quota, as a comma-separated list of group names.
* ``-R``/``--remove-groups``: disassociate one or more groups from
  the quota, as a comma-separated list of group names.

Previously deleted quotas can be restored using the
``-u``/``--undelete`` option.
