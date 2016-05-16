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
key pairs, by creating a ``.nebulizer`` file in your home directory, e.g.::

  % touch ~/.nebulizer

and populating with tab-delimited lines with ``alias|URL|API key``, for
example::

  localhost	http://127.0.0.1:8080	4af252f2250818d14949b3cf0aed476a

Then, rather than specifying the full URL and API key each you can just use
the alias, for example::

  % manage_users list localhost

instead of::

  % manage_users list http://127.0.0.1:8080 -k 4af252f2250818d14949b3cf0aed476a

Commands and usage examples
---------------------------

Currently ``nebulizer`` offers three utilities:

 * ``manage_users``: list and create user accounts
 * ``manage_libraries``: list, create and populate data libraries
 * ``manage_tools``: list and install tools from toolsheds

Some random examples (note that command names etc are subject to change
without notice while these utilities are under development):

Managing users
~~~~~~~~~~~~~~

Add a new user::

  manage_users create localhost -p pa55w0rd a.non@galaxy.org

List users matching specific name::

  manage_users list localhost --name=*briggs*

Managing data libraries
~~~~~~~~~~~~~~~~~~~~~~~

List data libraries::

  manage_libraries list localhost

Create a data library called ``NGS data`` and a subfolder ``Run 21``::

  manage_libraries create_library localhost \
    --description="Sequencing data analysed in 2015" "NGS data"
  manage_libraries create_folder localhost "NGS data/Run 21"

List contents of this folder::

  manage_libraries list localhost "NGS data/Run 21"

Upload files to it from the local system::

  manage_libraries add_datasets localhost "NGS data/Run 21" ~/Sample1_R*.fq

Add a file which is on the Galaxy server filesystem to a library as a
link::

  manage_libraries add_datasets localhost --server --link "NGS data/fastqs" \
    /galaxy/hosted_data/example.fq

Managing tools
~~~~~~~~~~~~~~

List all tools that are available in a Galaxy instance::

  manage_tools list localhost

List all the ``cuff...`` tools that were installed from a toolshed::

  manage_tools list localhost --name=cuff* --installed

List all the tool repositories that are installed along with the tools
that they provide::

  manage_tools installed localhost --list-tools

List all the tool repositories that have available updates or upgrades::

  manage_tools installed localhost --updateable

Install the most recent FastQC from the main toolshed::

  manage_tools install --tool-panel-section="NGS: QC and manipulation" \
    toolshed.g2.bx.psu.edu devteam fastqc

Update FastQC tool to latest installable revision::

  manage_tools update toolshed.g2.bx.psu.edu devteam fastqc

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

  manage_libraries list localhost -u joe.bloggs@example.com "NGS data/Run 21"

You will be prompted to enter the password; however you can also use the
``-P``/``--galaxy_password`` option to specify it explicitly on the command
line.
