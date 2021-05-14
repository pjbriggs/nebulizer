==================
Nebulizer Tutorial
==================

This tutorial offers a short hands-on introduction to the
main functionality offered by Nebulizer.


0. Preparation: making a temporary local Galaxy instance
--------------------------------------------------------

Before starting it is recommended to set up a temporary
local Galaxy instance to run the tutorial on, rather
than trying Nebulizer out on an existing installation.

The following commands should fetch and start up the
local instance:

::

   # Get the Galaxy source and put into a new directory
   # called 'galaxy_for_demo'
   git clone -b release_21.01 https://github.com/galaxyproject/galaxy.git galaxy_for_demo
   
   # Move into the source directory
   cd galaxy_for_demo

   # Make a configuration file
   cp config/galaxy.yml.sample config/galaxy.yml

You will need to edit the configuration file
``config/galaxy.yml`` using a text editor (e.g. ``vi``,
``nano``, ``gedit`` etc) to specify an admin user, by
changing the line:

::

   #admin_users: null

to e.g.

::

   admin_users: admin@localhost.org

or whatever email address you want. You will also need
to change the line:

::

   #allow_user_deletion: false

to

::

   allow_user_deletion: true

Then start Galaxy running:

::

   sh run.sh

.. note::

   This step can take some time when it's first run;
   however once Galaxy has installed its dependencies
   and performed its initial configuration then subsequent
   startups of the demo Galaxy should be much quicker.

   Use ``ctrl-C`` to stop Galaxy running, and repeat this
   command to start it up again.

Once Galaxy is running you can connect to it by pointing a
web browser to http://127.0.0.1:8080/

Finally you will need to register an account in Galaxy
with the same email address as the one used for
``admin_users`` (``admin@localhost.org`` in this example),
using the web browser.

Now you're ready to run through the tutorial.

.. note::
   
   Full instructions for setting up a local Galaxy
   instance can be found at
   https://galaxyproject.org/admin/get-galaxy/

1. Install Nebulizer
--------------------

Installing Nebulizer is best done in a Python virtual
environment - for example:

::

   virtualenv -p python3 venv.nebulizer
   . venv.nebulizer/bin/activate
   pip install nebulizer

.. note::

   It is recommended to do this in a different
   directory to the local Galaxy instance from
   the previous section.

Once this is done you should have access to the
``nebulizer`` utility.

To list the available commands:

::

   nebulizer --help

You use the ping command to check if a Galaxy instance
is active. For example to check the main Galaxy server:

::

   nebulizer ping https://usegalaxy.org

which should produce output like:

::

   https://usegalaxy.org: status = ok time = 574.041 (ms)
   https://usegalaxy.org: status = ok time = 587.883 (ms)
   https://usegalaxy.org: status = ok time = 549.526 (ms)
   ...

.. note::
   
   Do ``control-C`` to terminate the "ping".

You can also use the config command to query the details
of a Galaxy instance's configuration. For example to
query the local Galaxy:

::

   nebulizer config http://127.0.0.1:8080

2. Set up aliases for Galaxy API keys
-------------------------------------

Most Nebulizer commands require you to interact with
a Galaxy instance using an account on that instance.

For these commands you can authorise access each time
by specifying your registered email address and password
or Galaxy API key on the command line. For example:

::

   nebulizer -u admin@localhost.org whoami http://127.0.0.1:8080

.. note::

   ``-u`` will prompt you to enter the password for
   the account before performing the action; ``-k``
   can be used to specify the API key.

.. warning::

   This won't work if you didn't make an account
   for ``admin@localhost.org`` when preparing the
   local Galaxy in the previous step!

This is quite laborious when executing several commands,
so Nebulizer allows you to associate Galaxy instances and
their API keys with aliases; these are used as shortcuts
when running the commands.

To see the aliases and associated Galaxy servers:

::

   nebulizer list_keys

.. note::

   If you've never used Nebulizer before then nothing will
   be listed.

To set up a new alias called ``local`` and associate it with
the admin account in our local Galaxy, we can do:

::

   nebulizer -u admin@localhost.org add_key local http://127.0.0.1:8080

This will prompt you for the password for the account and
then create the alias. Once this is done you can repeat the
``list_keys`` command and see an entry for the local Galaxy:

::

   local  http://127.0.0.1:8080

In subsequent commands you can use ``local`` rather than
specifying the full Galaxy URL, and won't need to enter
your email or password. For example:

::

   nebulizer whoami local

Now we're ready to do some basic administration of our local
Galaxy using Nebulizer.

.. note::

   See :doc:`managing_keys` for more details.
   
3. Listing, adding and deleting users
-------------------------------------

We can list the users in our local Galaxy with:

::

   nebulizer list_users local

There will be just one account (the original admin account
we made at the start).

We can add a new user using:

::

   nebulizer create_user local ann.onymous@manchester.ac.uk

.. note::

   This will prompt you for a password for the new account;
   use the ``-p`` option to set the password via the
   command line.

Do the ``list_users`` command again to see new user listed.
Use the ``-l`` option to display additional information
about each user is displayed, including status and disk
usage (and quota usage, if quotas are enabled).

Batches of user accounts can be created from a "template"
name using the ``create_batch_users`` command; this can be
useful for example when setting up Galaxy instances for
teaching:

::

   nebulizer create_batch_users local user#@bcc2020.org 5

.. note::

   This will prompt you for a password which will be
   assigned to all the new accounts.

Use the ``list_users`` command to see the new accounts:

::

   user1@bcc2020.org              user1      
   user2@bcc2020.org              user2
   ...      
   user5@bcc2020.org              user5
   
Accounts can also be deleted:

::

   nebulizer delete_user local user5@bcc2020.org

The user will no longer be listed by ``list_users``.

.. warning::

   If the deletion fails then check that the Galaxy
   configuration has ``allow_user_deletion`` set
   to ``true``.

.. note::

   See :doc:`users` for more details.

4. Creating and populating data libraries
-----------------------------------------

We can list the data libraries in our local Galaxy
instance using:

::

   nebulizer list_libraries local

Initially our local Galaxy doesn't contain any library
data; we can create a new data library using:

::

   nebulizer create_library local "Example data"

.. note::

   Use the ``-d`` and ``-s`` options to add description
   and synopsis information for the new library.

Now this will be listed by the ``list_libraries`` command.
We can list the contents of a library by specifying its
name:

::

   nebulizer list_libraries local "Example data"

Initially the library is empty; we can create a folder
within the library:

::

   nebulizer create_library_folder local "Example data/Fastqs"

To list the contents of a library folder specify the
"path" to the folder:

::

   nebulizer list_libraries local "Example data/Fastqs"

Datasets can be added to libraries and folders from the
local workstation:

::

   nebulizer add_library_datasets local "Example data/Fastqs" Illumina_SG_R* --dbkey=hg38

.. note::

   The example Fastq files can be found here:

   * :download:`Illumina_SG_R1.fastq <tutorial_data/Illumina_SG_R1.fastq>`
   * :download:`Illumina_SG_R2.fastq <tutorial_data/Illumina_SG_R2.fastq>`
   
When listing the contents of libraries and folders,
additional information is reported by specifying the ``-l``
option:

::

   nebulizer list_libraries local "Example data/Fastqs" -l

.. note::

   See :doc:`libraries` for more details.

5. Installing and managing tools
--------------------------------

We can list the tools installed in our local Galaxy using:

::

   nebulizer list_tools local

Initially there are no tools installed; we can search the
main Galaxy toolshed for the tools we want to install,
for example the FastQC tool:

::

   nebulizer search_toolshed fastqc

.. warning::

   The time taken for searching depends on the speed
   of the toolshed, so sometimes this can be slow if
   e.g. the toolshed is experiencing issues.

This will list all the tool repositories and toolshed
versions available to install:

::

    devteam  fastqc  21:e7b2202befea   
    devteam  fastqc  19:9da02be9c6cc   
    devteam  fastqc  16:ff9530579d1f
    ...
   
We can install the latest version of FastQC with

::

   nebulizer install_tool local devteam/fastqc --tool-panel-section="NGS tools"

.. note::

   Using ``--tool-panel-section`` will create a new section
   in the Galaxy tool panel and put the tools from this
   repository under it; otherwise tools are not installed
   under any section. You can use the ``list_tool_panel``
   command to see what tool panel sections are already
   present.

Running ``list_tools`` now shows the tool repository is
installed:

::

   * fastqc  toolshed.g2.bx.psu.edu  devteam  21:e7b2202befea  Installed

.. note::

   The ``*`` next to tool repository indicates that this
   is most recent version.

   Use the ``--mode=tools`` option to list the associated
   tools instead.

We can install a specific version of a tool repository, for
example the Trimmomatic tool:

::

   nebulizer install_tool local pjbriggs/trimmomatic 51b771646466 --tool-panel-section="NGS tools"

Running ``list_tools`` now shows this tool repository is also
installed:

::

   * fastqc       toolshed.g2.bx.psu.edu  devteam   21:e7b2202befea  Installed
   U trimmomatic  toolshed.g2.bx.psu.edu  pjbriggs  12:51b771646466  Installed

Here ``U`` indicates there is a newer revision available
with a new version of the tool (``u`` indicates a newer
revision without a tool version update).

Rerunning the ``list_tools`` command with the ``--updateable``
option filters the list of tool repositories to just those with
available updates.

We can update Trimmomatic to the newest version automatically
by running the ``update_tool`` command:

::

   nebulizer update_tool local pjbriggs/trimmomatic

.. note::

   This installs the most recent version but doesn't
   remove the older version.

The ``uninstall_tool`` command removes an installed
repository; for example to uninstall the older Trimmomatic
tool version:

::

   nebulizer uninstall_tool local pjbriggs/trimmomatic 51b771646466

Running ``list_tools`` shows that the older tool repository
is no longer present.

.. note::

   See :doc:`tools` for more details.

