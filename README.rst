nebulizer
=========

``nebulizer`` is a set of command line utilities to help with managing users,
data libraries and tools in a `Galaxy <https://galaxyproject.org/>`_
instance, using the Galaxy API via the `Bioblend
<http://bioblend.readthedocs.org/en/latest/>`_ Python library.

**Caveat**

 * This is very much a work in progress, and operations such as user or library
   creation and tool installation should be used with caution against production
   instances of Galaxy.

Installation
------------

It is recommended to install ``nebulizer`` via ``pip`` in a virtualenv, for
example::

  % virtualenv .venv; . .venv/bin/activate
  % pip install git+https://github.com/pjbriggs/nebulizer.git

Setup
-----

Although ``nebulizer``'s commands can be used without additional setup, it is
possible to create shortcuts in the form of 'aliases' to Galaxy URLs and API
key pairs, which are stored in a ``.nebulizer`` file in your home directory.

This can be managed using the ``nebulizer`` utility, e.g. to add new alias
for a local Galaxy instance::

  % nebulizer add_key localhost http://127.0.0.1:8080 4af252f2250818d14949b3cf0aed476a

Alternatively: if you don't have the API key then nebulizer will fetch it
if you give it a user name, for example::

  % nebulizer -u me@example.org add_key localhost http://127.0.0.1:8080

Each alias is stored in a tab-delimited line with the format
``alias|URL|API key``, for example::

  localhost	http://127.0.0.1:8080	4af252f2250818d14949b3cf0aed476a

Then, rather than specifying the full URL and API key each you can just use
the alias, for example::

  % nebulizer list_users localhost

instead of::

  % nebulizer -k 4af252f2250818d14949b3cf0aed476a list_users http://127.0.0.1:8080

See below for more information on managing the stored aliases and
associated information.

Commands
--------

All functionality is available as subcommands of the ``nebulizer``
utility.

User management:

 * ``list_users``: List users in Galaxy instance.
 * ``create_user``: Create new Galaxy user.
 * ``create_batch_users``: Create multiple Galaxy users from a template.
 * ``create_users_from_file``: Create multiple Galaxy users from a file.

Data library management:

 * ``list_libraries``:  List data libraries and contents.
 * ``create_library``: Create new data library.
 * ``create_library_folder``: Create new folder in a data library.
 * ``add_library_datasets``: Add datasets to a data library.

Tool data tables management:

 * ``list_data_tables``:  List data tables in Galaxy instance.
 * ``show_data_table``: Show tool data table contents.

Tool management:

 * ``list_tools``: List tools in Galaxy instance.
 * ``list_tool_panel``: List tool panel contents.
 * ``list_installed_tools``: List installed tool repositories.
 * ``install_tool``: Install tool from toolshed.
 * ``update_tool``: Update tool installed from toolshed.

Local API key management:

 * ``add_key``: Store new Galaxy URL and API key.
 * ``list_keys``: List stored Galaxy API keys.
 * ``remove_key``: Remove stored Galaxy API key.
 * ``update_key``: Update stored Galaxy API key.

Deprecated utilities
~~~~~~~~~~~~~~~~~~~~

The following additional utilities are included for backwards
compatibility but are deprecated and likely to be removed in a
future version:

 * ``manage_users``: list and create user accounts
 * ``manage_libraries``: list, create and populate data libraries
 * ``manage_tools``: list and install tools from toolsheds

They are not documented further here.

Usage examples
--------------

The following sections have usage examples intended to give a
flavour of how ``nebulizer`` might be used.

Managing users
~~~~~~~~~~~~~~

List users matching specific name::

  nebulizer list_users localhost --name="*briggs*"

Add a new user::

  nebulizer create_user localhost -p pa55w0rd a.non@galaxy.org

Managing data libraries
~~~~~~~~~~~~~~~~~~~~~~~

List data libraries::

  nebulizer list_libraries localhost

Create a data library called ``NGS data`` and a subfolder ``Run 21``::

  nebulizer create_library localhost \
    --description="Sequencing data analysed in 2015" "NGS data"
  nebulizer create_library_folder localhost "NGS data/Run 21"

List contents of this folder::

  nebulizer list_libraries localhost "NGS data/Run 21"

Upload files to it from the local system::

  nebulizer add_library_datasets localhost "NGS data/Run 21" ~/Sample1_R*.fq

Add a file which is on the Galaxy server filesystem to a library as a
link::

  nebulizer add_library_datasets localhost --server --link "NGS data/fastqs" \
    /galaxy/hosted_data/example.fq

Managing tools
~~~~~~~~~~~~~~

List all tools that are available in a Galaxy instance::

  nebulizer list_tools localhost

List all the ``cuff...`` tools that were installed from a toolshed::

  nebulizer list_tools localhost --name="cuff*" --installed

List all the tool repositories that are installed along with the tools
that they provide::

  nebulizer list_installed_tools localhost --list-tools

List all the tool repositories that have available updates or upgrades::

  nebulizer list_installed_tools localhost --updateable

Install the most recent FastQC from the main toolshed::

  nebulizer install_tool localhost \
    --tool-panel-section="NGS: QC and manipulation" \
    toolshed.g2.bx.psu.edu devteam fastqc

Update FastQC tool to latest installable revision::

  nebulizer update_tool localhost toolshed.g2.bx.psu.edu devteam fastqc

Managing Galaxy API keys
~~~~~~~~~~~~~~~~~~~~~~~~

List the stored aliases and associated Galaxy instances::

  nebulizer list_keys

Add a new alias called 'production' for a Galaxy instance::

  nebulizer add_key production http:://galaxy.org/ 5e7a1264905c8f0beb80002f7de13a40

Update the API key for 'production'::

  nebulizer update_key production --new-api-key=37b6430624255b8c61a137abd69ae3bb

Remove the entry for 'production'::

  nebulizer remove_key production

Handling SSL certificate failures
---------------------------------

``nebulizer`` commands will fail for Galaxy instances which are served over
``https`` protocol without a valid SSL certificate, reporting an error like::

  [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:590), 0 attempts left: None

In this case adding the ``--no-verify`` (``-n``) option turns off the
certificate verification and should enable a connection to be made.

Using email and password instead of API key
-------------------------------------------

It is possible to use your normal Galaxy login credentials (i.e. your email
and password) to access the API on a Galaxy instance without using the
API key, using the ``-u``/``--username`` option, e.g.::

  nebulizer -u joe.bloggs@example.com list_libraries "NGS data/Run 21"

You will be prompted to enter the password; however you can also use the
``-P``/``--galaxy_password`` option to specify it explicitly on the command
line.
