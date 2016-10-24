History
-------

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
