.. figure:: https://raw.githubusercontent.com/pjbriggs/nebulizer/master/docs/nebulizer_logo.png
   :alt: Nebulizer Logo
   :align: center
   :figwidth: 100%
   :target: https://github.com/pjbriggs/nebulizer

Command-line utilities to help with managing users, data libraries and
tools in a `Galaxy <https://galaxyproject.org/>`_ instance, using the
Galaxy API via the `Bioblend <http://bioblend.readthedocs.org/en/latest/>`_
library.

.. image:: https://readthedocs.org/projects/pip/badge/?version=latest
   :target: https://nebulizer.readthedocs.io

.. image:: https://badge.fury.io/py/nebulizer.svg
   :target: https://pypi.python.org/pypi/nebulizer/

.. image:: https://travis-ci.org/pjbriggs/nebulizer.png?branch=master
   :target: https://travis-ci.org/pjbriggs/nebulizer

* Free software: Academic Free License version 3.0
* Documentation: https://nebulizer.readthedocs.io
* Code: https://github.com/pjbriggs/nebulizer

.. warning::

   **CAVEAT** ``nebulizer`` is still a work in progress; please exercise
   caution when attempting irreversible operations especially against
   production Galaxy instances (for example when creating users or data
   libraries).

Quick Start
-----------

This quick start gives some examples of using ``nebulizer`` commands
to perform remote administration tasks on a Galaxy instance from the
command line.

-----------------
Getting Nebulizer
-----------------

It is recommended to install Nebulizer via ``pip`` in a virtualenv,
for example::

  % virtualenv .venv; . .venv/bin/activate
  % pip install nebulizer

This will provide an executable called ``nebulizer`` with a number
of subcommands for performing different tasks remotely on Galaxy
instances.

----------------
Nebulizer Basics
----------------

To interact remotely with a Galaxy instance using Nebulizer requires
at minimum the URL of the instance and then either an API key or a
user login name.

For example to list data libraries available on Galaxy Main::

  % nebulizer -k 9b376af2250818d14949b3c list_libraries https://usegalaxy.org

or::

  % nebulizer -u peter.briggs@manchester.ac.uk list_libraries https://usegalaxy.org

(in this second case ``nebulizer`` will prompt for the Galaxy
password to authenticate the user login.)

Specifying full API keys and Galaxy URLs each time a command is run
is tedious, so Nebulizer can store URL-key pairs locally to make this
easier.

For example to store the API key for Galaxy main::

  % nebulizer add_key main https://usegalaxy.org 9b376af2250818d14949b3c

stores the API key and URL pair and associates it with the alias ``main``.

Alternatively Nebulizer can fetch the API key itself if the user
login is provided instead, for example::

  % nebulizer -u peter.briggs@manchester.ac.uk add_key main https://usegalaxy.org

The stored alias can then be used as a substitute for the URL with the
the stored API key being fetched behind the scenes. Then to list the
data libraries again it is sufficient to do just::

  % nebulizer list_libraries main

The following sections contain examples of how Nebulizer might be
used to perform various administrive tasks.

--------------
Managing Users
--------------

List users matching specific name::

  nebulizer list_users galaxy --name="*briggs*"

Add a new user::

  nebulizer create_user galaxy -p pa55w0rd a.non@galaxy.org

-----------------------
Managing Data Libraries
-----------------------

List data libraries::

  nebulizer list_libraries galaxy

Create a data library called ``NGS data`` and a subfolder ``Run 21``::

  nebulizer create_library galaxy \
    --description="Sequencing data analysed in 2015" "NGS data"
  nebulizer create_library_folder localhost "NGS data/Run 21"

List contents of this folder::

  nebulizer list_libraries galaxy "NGS data/Run 21"

Upload files to it from the local system::

  nebulizer add_library_datasets galaxy "NGS data/Run 21" ~/Sample1_R*.fq

Add a file which is on the Galaxy server filesystem to a library as a
link::

  nebulizer add_library_datasets galaxy --server --link "NGS data/fastqs" \
    /galaxy/hosted_data/example.fq

--------------
Managing Tools
--------------

List all tools that are available in a Galaxy instance::

  nebulizer list_tools galaxy

List all the ``cuff...`` tools that were installed from a toolshed::

  nebulizer list_tools galaxy --name="cuff*" --installed

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

Commands
--------

All functionality is available as subcommands of the ``nebulizer``
utility.

---------------
User Management
---------------

 * ``list_users``: List users in Galaxy instance.
 * ``create_user``: Create new Galaxy user.
 * ``create_batch_users``: Create multiple Galaxy users from a template.
 * ``create_users_from_file``: Create multiple Galaxy users from a file.

-----------------------
Data Library Management
-----------------------

 * ``list_libraries``:  List data libraries and contents.
 * ``create_library``: Create new data library.
 * ``create_library_folder``: Create new folder in a data library.
 * ``add_library_datasets``: Add datasets to a data library.

---------------
Tool Management
---------------

 * ``list_tools``: List tools in Galaxy instance.
 * ``list_tool_panel``: List tool panel contents.
 * ``list_installed_tools``: List installed tool repositories.
 * ``install_tool``: Install tool from toolshed.

-------------------------------
Bulk Tool Repository Management
-------------------------------

 * ``list_repositories``: List installed tool repos for (re)install.
 * ``install_repositories``: Install tool repositories listed in a file.

------------------------
Local API Key Management
------------------------

 * ``add_key``: Store new Galaxy URL and API key.
 * ``list_keys``: List stored Galaxy API keys.
 * ``remove_key``: Remove stored Galaxy API key.
 * ``update_key``: Update stored Galaxy API key.

Hints and Tips
--------------

------------------------
Managing Galaxy API keys
------------------------

Nebulizer stores the URL-key pairs in the file ``.nebulizer``
located in the user's home directory. This file consists of
tab-delimited lines with the following columns::

  alias|Galaxy_URL|API_key

This file can be edited by hand using a text editor such as
``vi``; however Nebulizer provides a set of commands for
querying and modifying the file contents.

To list the stored aliases with associated Galaxy URLs and
API keys::

  % nebulizer list_keys

To add a new alias called 'production' for a Galaxy instance::

  nebulizer add_key production http:://galaxy.org/ 5e7a1264905c8f0beb80002f7de13a40

Update the API key for 'production'::

  nebulizer update_key production --new-api-key=37b6430624255b8c61a137abd69ae3bb

Remove the entry for 'production'::

  nebulizer remove_key production

Multiple URL-key pairs can be stored; only the associated
aliases need to be unique. For example::

  % nebulizer -u admin@galaxy.org add_key palfinder https://palfinder.ls.manchester.ac.uk
  ...prompt for password...
  % nebulizer list_libraries palfinder

----------------------------------------------
Handling SSL Certificate Verification Failures
----------------------------------------------

Nebulizer commands will fail for Galaxy instances which are served over
``https`` protocol without a valid SSL certificate, reporting an error like::

  [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:590), 0 attempts left: None

In this case adding the ``--no-verify`` (``-n``) option turns off the
certificate verification and should enable a connection to be made.

---------------------------------------------------------
Accessing Galaxy with Email & Password instead of API key
---------------------------------------------------------

It is possible to use your normal Galaxy login credentials (i.e. your email
and password) to access the API on a Galaxy instance without using the
API key, using the ``-u``/``--username`` option, e.g.::

  nebulizer -u joe.bloggs@example.com list_libraries "NGS data/Run 21"

You will be prompted to enter the password; however you can also use the
``-P``/``--galaxy_password`` option to specify it explicitly on the command
line.

-------------------------------------------------
Installing Multiple Tool Repositories from a List
-------------------------------------------------

It is possible to install a list of tool repositories into a
Galaxy instance by using the ``install_repositories`` command::

  nebulizer install_repositories galaxy tools.tsv

The ``tools.tsv`` file must be a tab-delimited list of repositories,
one repository per line in the format::

  TOOLSHED|OWNER|REPOSITORY|REVISON|SECTION

For example::

  toolshed.g2.bx.psu.edu	devteam	bowtie_wrappers	9ca609a2a421	NGS: Mapping

A list of tool repositories already installed in a Galaxy instance
can be generated in this format using the ``list_repositories``
command::

  nebulizer list_repositories galaxy > tools.tsv

In principle the combination of these two commands can be used to
'clone' the installed tools from one Galaxy instance into another.

For example to replicate the tools installed on the 'Palfinder'
instance::

  nebulizer list_repositories https://palfinder.ls.manchester.ac.uk > palfinder.tsv
  nebulizer install_repositories http://127.0.0.1 palfinder.tsv

Deprecated Utilities
--------------------

The following additional utilities are included for backwards
compatibility but are deprecated and likely to be removed in a
future version:

 * ``manage_users``: list and create user accounts
 * ``manage_libraries``: list, create and populate data libraries
 * ``manage_tools``: list and install tools from toolsheds

They are not documented further here.

License
-------

Nebulizer is licensed under the `Academic Free License (AFL) <https://opensource.org/licenses/AFL-3.0>`_.
