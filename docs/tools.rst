==============
Managing Tools
==============

Querying tool information
-------------------------

By default, ``list_tools`` displays information on all the tool
repositories that are installed in a Galaxy instance:

::

  nebulizer list_tools GALAXY

For each installed repository the details include: repository name,
toolshed, owner, revision id and changeset, and installation status.

Repository details are also preceeded by a single-character 'status'
indicator:

* ``D`` = deprecated;
* ``^`` = newer revision is also installed;
* ``u`` = update (newer revision) is available but not installed;
* ``U`` = upgrade available (new revision with a change of tool
  version) but not installed;
* ``*`` = latest revision installed

``list_tools`` supports a number of options to modify its
behaviour, including:

* ``--updateable``: only list tool repositories that have uninstalled
  available updates or upgrades
* ``--built-ins``: include details of the "built-in" tools within the
  Galaxy instance (i.e. those not installed from a toolshed)

An alternative 'tool-centric' view of the tools in a Galaxy instance
can be obtained using the ``--mode=tools`` option.

.. note::
   
   This is a new version of the ``list_tools`` which replaces the
   old ``list_installed_tools`` command (which is no longer
   available). The ``--mode=tools`` option replicates the output
   from the old ``list_tools`` command.

``list_tool_panel`` displays information on the tool panel
sections in a Galaxy instance:

::

   nebulizer list_tool_panel GALAXY

New tool panel sections can be created when installing tool
repositories.
  
Install, update and remove tools
--------------------------------

``install_tool`` installs tools from a Galaxy toolshed (by default
the main Galaxy toolshed at https://toolshed.g2.bx.psu.edu):

::
   
   nebulizer install_tool GALAXY TOOL_REPOSITORY

The tool repository can be specified as:

* ``[TOOLSHED] OWNER/TOOLNAME [ REVISION ]`` e.g.
  ``devteam/fastqc`` (defaults to most recent revision from the
  main toolshed), or ``devteam/fastqc e7b2202befea`` (specifies
  revision ``e7b2202befea``)
* toolshed URL with or without a revision (e.g.
  ``https://toolshed.g2.bx.psu.edu/view/devteam/fastqc/e7b2202befea``)
   
* ``--tool-panel-section``: specify a tool panel section to
  install the tools from the repository into (otherwise tools
  appear at the "top level" of the tool panel)

For example: to install the most recent FastQC tool from the main
Galaxy toolshed under the ``NGS: QC and manipulation`` section of
the tool panel:

::

   nebulizer install_tool GALAXY devteam/fastqc \
      --tool-panel-section="NGS: QC and manipulation"

To install a specific revision of the Trimmer tool from the
test toolshed:

::

   nebulizer install_tool GALAXY \
      https://testtoolshed.g2.bx.psu.edu/view/devteam/trimmer/dec27ea206c3 \
      --tool-panel-section="Test tools"


``update_tool`` installs the latest revision of a previously
installed tool repository, if a new version is available:

::

   nebulizer update_tool GALAXY TOOL_REPOSITORY

The tool repository is specified as with ``install_tool``
except that a revision cannot be included. For example:

::

   nebulizer update_tool GALAXY devteam/fastqc

It is also possible to include glob-style wildcards in the
tool repository name and/or owner e.g. ``devteam/*`` or
``bgruening/deeptools_*``. To request update of all tools:

::

   nebulizer update_tool GALAXY '*/*'

.. note::

   ``update_tool`` doesn't uninstall the older versions of
   the tools that are updated.

.. warning::

   By default checks on the availability of updates for tools
   performed by the ``list_tools`` and ``update_tool``
   commands are done using information cached by the Galaxy
   instance in question. As a result these commands may not
   always indicate when updates are available.

   To force these commands to check the installed revisions
   against those in the toolshed, add the ``--check-toolshed``
   option. Note however that this can impose a significant
   overhead which can make the commands much slower.

``uninstall_tool`` removes a previously installed tool:

::

   nebulizer uninstall_tool GALAXY TOOL_REPOSITORY

The tool repository is specified as with ``install_tool``,
for example to uninstall and deactivate a specific revision
of a tool:

::

   nebulizer uninstall_tool GALAXY devteam/fastqc/e7b2202befea

To uninstall all installed revisions of a tool and remove from
disk:

::

   nebulizer uninstall_tool localhost devteam/fastqc/* \
      --remove_from_disk


Searching for tool repositories on a Toolshed
---------------------------------------------

``search_toolshed`` searches for tools on a toolshed:

::
   
   nebulizer search_toolshed QUERY

``QUERY`` can include glob-style wildcards. For example, to
search the main toolshed for Deeptools related tools:

::

    nebulizer search_toolshed "deeptools_*"

* ``--toolshed``: specify the URL of the toolshed to
  search.


Bulk tool repository management
-------------------------------

``install_tool --file`` installs the tool repositories listed in
a tab-delimited file into a Galaxy instance:

::

   nebulizer install_tool GALAXY TOOLS_FILE

``TOOLS_FILE`` must be a tab-delimited list of repositories,
one repository per line in the format:

::

   TOOLSHED|OWNER|REPOSITORY|REVISON|SECTION

For example:

::

  toolshed.g2.bx.psu.edu	devteam	bowtie_wrappers	9ca609a2a421	NGS: Mapping


``list_tools --mode=export`` can generate a list of tool repositories
already installed in a Galaxy instance in this format, e.g.:

::

   nebulizer list_tools GALAXY --mode=export

By combining these two commands it is possible to 'clone' the
installed tools from one Galaxy instance into another.

For example to replicate the tools installed on the 'Palfinder'
instance into a local Galaxy:

::

  nebulizer list_tools https://palfinder.ls.manchester.ac.uk --mode=export > palfinder.tsv
  nebulizer install_tool http://127.0.0.1 --file palfinder.tsv

.. warning::

   Bulk installation of tools in this manner should be used with
   caution, especially when installing into a Galaxy instance
   which already has installed tools.
