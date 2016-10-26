History
-------

-------------------
v0.3.0 (2016-10-26)
-------------------

 * New class ``tools.ToolPanel`` and updates to existing
   ``tools.ToolPanelSection`` clas.
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
