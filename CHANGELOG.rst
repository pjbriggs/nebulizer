History
-------

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
   (`PR #23 <https://github.com/pjbriggs/nebulizer/pull/23`_)
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
