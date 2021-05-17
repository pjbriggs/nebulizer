History
-------

-------------------
v0.7.0 (2021-05-17)
-------------------

**Breaking changes:**

 * Dropped support for Python 2.7: ``nebulizer`` now needs
   Python 3.6+ (thanks to Hugo van Kemenade @hugovk)
   (`PR #102 <https://github.com/pjbriggs/nebulizer/pull/102>`_)
 * Substantial refactoring and simplification of the tool
   managament commands
   (`PR #113 <https://github.com/pjbriggs/nebulizer/pull/113>`_):
   - Now only ``list_tools``, ``install_tool``, ``update_tool``
     and ``delete_tool`` commands are supported
   - ``list_installed_tools`` renamed to ``list_tools``
   - old functionality of ``list_tools`` replaced by
     ``list_tools --mode=tools``
   - ``list_repositories`` command dropped; functionality
     replaced by ``list_tools --mode=export``
   - ``install_repositories`` command dropped; functionality
     replaced by ``install_tool --file=...``

**New commands:**

 * New ``quota``, ``quota_add``, ``quota_mod`` and ``quota_del``
   commands for managing quotas
   (`PR #66 <https://github.com/pjbriggs/nebulizer/pull/66>`_)

**Updates to existing commands:**

 * ``-l`` option for ``search_toolshed`` includes the shed URL
   (`PR #91 <https://github.com/pjbriggs/nebulizer/pull/91>`_)
 * ``update_tool`` allows use of wildcards (i.e. ``*``) when
   specifying tool repository names and owners, to enable
   multiple tool repositories to updated at once
   (`PR #92 <https://github.com/pjbriggs/nebulizer/pull/92>`_)
 * New ``--status`` option for ``list_users`` command allows
   deleted and purged user accounts to also be listed
   (`PR #97 <https://github.com/pjbriggs/nebulizer/pull/97>`_)
 * New ``--sort`` option for ``list_users`` command allows
   sorting of listed accounts by disk usage, quota and quota
   usage
   (`PR #104 <https://github.com/pjbriggs/nebulizer/pull/104>`_)

**Bug fixes:**

 * Fix to using the ``--purge`` option of the ``delete_user``
   command (previously it wasn't possible to purge accounts)
   (`PR #98 <https://github.com/pjbriggs/nebulizer/pull/98>`_)
 * Remove requirement to specify an account or API key on
   Galaxy server when using the ``ping`` and ``config`` commands
   (`PR #100 <https://github.com/pjbriggs/nebulizer/pull/100>`_)

**Other updates:**

 * Added support for Python 3.9 (thanks to Hugo van Kemenade
   @hugovk)
   (`PR #108 <https://github.com/pjbriggs/nebulizer/pull/108>`_)

-------------------
v0.6.0 (2020-07-14)
-------------------

**New commands:**

 * New ``search_toolshed`` command
   (`PR #42 <https://github.com/pjbriggs/nebulizer/pull/42>`_)
 * New ``config`` command
   (`PR #57 <https://github.com/pjbriggs/nebulizer/pull/57>`_)
 * New ``delete_user`` command
   (`PR #62 <https://github.com/pjbriggs/nebulizer/pull/62>`_)
 * New ``uninstall_tool`` command
   (`PR #64 <https://github.com/pjbriggs/nebulizer/pull/64>`_)

**Updates to existing commands:**

 * ``list_keys`` doesn't report API keys unless
   ``--show-api-keys`` option is specified
   (`PR #58 <https://github.com/pjbriggs/nebulizer/pull/58>`_)
 * Additional fields reported by ``--long-listing-format``
   option of ``list_users`` (disk and quota usage, status);
   doesn't report ID by default
   (`PR #59 <https://github.com/pjbriggs/nebulizer/pull/59>`_)
 * Enable flexible tool repository specification syntax for
   ``install_tool`` and ``update_tool``
   (`PR #60 <https://github.com/pjbriggs/nebulizer/pull/60>`_)
 * ``remove_key`` prompts user to confirm API key deletion
   (`PR #72 <https://github.com/pjbriggs/nebulizer/pull/72>`_)
 * Use spaces rather than tabs to line up fields in output
   from ``list_users``, ``list_installed_tools``,
   ``list_tools``, ``list_tool_panel``, ``list_keys``, ``config``,
   ``list_libraries``; use ``--show_id`` to report Galaxy
   IDs for users and data libraries
   (`PR #68 <https://github.com/pjbriggs/nebulizer/pull/68>`_,
   `PR #69 <https://github.com/pjbriggs/nebulizer/pull/69>`_,
   `PR #70 <https://github.com/pjbriggs/nebulizer/pull/70>`_)

**Documentation:**

 * Add a tutorial/walkthrough
   (`PR #75 <https://github.com/pjbriggs/nebulizer/pull/75>`_)
 * Significant overhaul and expansion of documentation
   (`PR #78 <https://github.com/pjbriggs/nebulizer/pull/78>`_)

**Removed functionality:**

 * Removed deprecated utilities ``manage_users``,
   ``manage_tools`` and ``manage_libraries``
   (`PR #61 <https://github.com/pjbriggs/nebulizer/pull/61>`_)

-------------------
v0.5.0 (2020-04-20)
-------------------

 * Add support for Python 3.6, 3.7 and 3.8
   (`PR #50 <https://github.com/pjbriggs/nebulizer/pull/50>`_,
   `PR #51 <https://github.com/pjbriggs/nebulizer/pull/51>`_)

-------------------
v0.4.3 (2018-10-05)
-------------------

 * Ensure that ``click`` dependency is version 6.7 or earlier, to
   avoid subcommand names changing from e.g. ``list_users`` to
   ``list-users``
   (`PR #49 <https://github.com/pjbriggs/nebulizer/pull/49>`_)

-------------------
v0.4.2 (2017-08-24)
-------------------

 * Commands now explicitly return appropriate exit code values
   indicating success (``0``) or failure (non-zero values).
 * New option ``--check-toolshed`` added to ``list_installed_tools``
   and ``update_tool`` commands, to check installed revisions directly
   against those available in the toolshed
   (`PR #41 <https://github.com/pjbriggs/nebulizer/pull/41>`_)
 * Update ``install_tool``, ``update_tool`` and ``install_repositories``
   to install tool dependencies through a resolver (e.g. ``conda``)
   by default
   (`issue #43 <https://github.com/pjbriggs/nebulizer/issues/43>`_)
 * New options added to ``install_tool``, ``update_tool`` and
   ``install_repositories`` commands, to explicit control how tool
   and repository dependencies should be handled
   (`PR #44 <https://github.com/pjbriggs/nebulizer/pull/44>`_):

   - ``--install-tool-dependencies [yes|no]``: install tool
     dependencies via the toolshed, if any are defined (default is
     ``yes``)
   - ``--install-tool-dependencies [yes|no]``: install tool
     dependencies via the toolshed, if any are defined (default is
     ``yes``)
   - ``--install-resolver-dependencies [yes|no]``: install
     dependencies through a resolver that supports installation (e.g.
     ``conda``) (default is ``yes``)

-------------------
v0.4.1 (2016-12-19)
-------------------

 * Fix broken ``update_tool`` command
   (`PR #40 <https://github.com/pjbriggs/nebulizer/pull/40>`_).

-------------------
v0.4.0 (2016-11-18)
-------------------

 * New subcommand ``ping``: 'ping' a Galaxy instance to see if it's
   responsive
   (`PR #33 <https://github.com/pjbriggs/nebulizer/pull/33>`_).
 * New subcommand ``whoami``: reports user associated with the API
   key
   (`PR #37 <https://github.com/pjbriggs/nebulizer/pull/37>`_).
 * ``add_library_datasets``: refuses to perform upload if using the
   master API key (essentially API key must have an associated user).
 * ``install_repositories``: prints a list of all tool repositories
   that couldn't be installed.
 * New ``--timeout`` and ``--nowait`` options added for
   ``install_tool``, ``update_tool`` and ``install_repositories``
   subcommands.
 * Fix to treat tool repositories with status ``New`` as still
   installing when trying to install tools
   (`PR #31 <https://github.com/pjbriggs/nebulizer/pull/31>`_).
 * Some improvements to logging
   (`PR #38 <https://github.com/pjbriggs/nebulizer/pull/38>`_).

-------------------
v0.3.0 (2016-10-26)
-------------------

 * New class ``tools.ToolPanel`` and updates to existing
   ``tools.ToolPanelSection`` class.
 * ``install_tool``: fix behaviour so that command does nothing if
   a version is not specified and at least one version of the tool is
   already installed.
 * ``list_repositories`` and ``install_repositories``: new commands
   to generate a list of installed tool repositories from a Galaxy
   instance and then reinstall tool repositories from a list with
   the same format
   (`PR #19 <https://github.com/pjbriggs/nebulizer/pull/19>`_).
 * ``install_tool``: fix incorrect reporting of target tool panel
   section
   (`PR #20 <https://github.com/pjbriggs/nebulizer/pull/20>`_)
 * ``add_key`` and ``update_key``: fix automatic retrieval of API
   key, which only worked previously if connecting user was an
   admin account
   (`PR #23 <https://github.com/pjbriggs/nebulizer/pull/23>`_)
 * ``list_tool_panel``: shows tools in order they appear in Galaxy
   when using ``--list-tools`` option.
 * Deprecated utilities (``manage_users``, ``manage_tools`` and
   ``manage_libraries``) issue warnings when run.
 * License updated to Academic Free License (AFL).
 * Initial version of documentation also made available via
   `ReadTheDocs <http://nebulizer.readthedocs.io>`_
   (`PR #21 <https://github.com/pjbriggs/nebulizer/pull/21>`_)

-------------------
v0.2.0 (2016-10-17)
-------------------

 * Implemented new ``nebulizer`` utility which provides all previous
   functionality via subcommands, plus commands for managing API keys
   automatically (old ``manage_users``, ``manage_tools`` and
   ``manage_libraries`` utilities are still available for
   backwards-compatibility but are deprecated).
 * New general options:

   - ``-q``/``--suppress-warnings``: prevent warning messages from
     ``nebulizer`` commands.

 * Various fixes and improvements to underlying functionality:

   - ``install_tools``: now checks if tool is already installed;
     handles tool revisions that include the revision number; polls
     Galaxy until tool is installed, or operation times out; exit
     status reflects the success or failure of the installation.
   - ``update_tool``: now works even if original tool isn't in a tool
     panel section
   - ``list_installed_tools``: now groups tools under correct repo
     revision when using ``--list-tools`` option.

-------------------
v0.1.1 (2016-05-16)
-------------------

 * Add ``-u``/``--username`` and ``-P``/``--galaxy_password`` options
   to all commands to allow interaction with Galaxy instance via API
   using normal login credentials instead of API key.

-------------------
v0.1.0 (2015-11-06)
-------------------

 * Initial release of ``nebulizer`` utilities for administering
   Galaxy instances via the command line.
