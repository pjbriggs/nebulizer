=======================
Managing Data Libraries
=======================

Querying data libraries
-----------------------

``list_libraries`` displays information about the data libraries
and their contents in a Galaxy instance:

::

   nebulizer list_libraries GALAXY [ LIBRARY[/PATH...] ]

By default all the libraries in the instance are listed; if the
name of a data library (``LIBRARY``) is included then the datasets
and folders in that library are listed. If a ``PATH`` (names of
subfolders separated by ``/``) is supplied then the contents of
the matching folder are displayed.

For example: listing the data libraries in Galaxy main:

::

   nebulizer list_libraries https://usegalaxy.org

List the contents of the "Tutorials" data library:

::

   nebulizer list_libraries https://usegalaxy.org Tutorials

List the contents of the "ChIP_seq (Reb1)" folder in the
"Tutorials" data library:

::

   nebulizer list_libraries https://usegalaxy.org "Tutorial/ChIP_seq (Reb1)"

* ``-l``: list extended information about libraries, folders
  and datasets

Creating and populating data libraries
--------------------------------------

``create_library`` creates a new data library:

::

   nebulizer create_library GALAXY LIBRARY_NAME [--description DESCRIPTION] [--synopsis SYNOPSIS]

``create_library_folder`` creates a new folder in an existing
data library or folder:

::

   nebulizer create_library_folder GALAXY LIBRARY_NAME/[PATH]

For example: create a data library called ``NGS data`` and a folder
``Run 21`` within it:

::

  nebulizer create_library GALAXY "NGS data 2020" \
    --description="Sequencing data analysed in 2020"
  nebulizer create_library_folder GALAXY "NGS data 2020/Run 21"

``add_library_datasets`` uploads datasets to a data library:

::

   nebulizer add_library_datasets GALAXY LIBRARY_NAME/PATH FILE [FILE...]

* ``--file-type``: specify the Galaxy data type to assign to
  datasets
* ``--dbkey``: specify the dbkey for the datasets
* ``--server``: upload files from the filesystem of the server
  that Galaxy is running on (default is to upload from the local
  filesystem)
* ``--link``: create symlinks to the files on the server (if
  ``--server`` is also specified)

For example, add Fastq files to a data library folder:

::

  nebulizer add_library_datasets galaxy "NGS data/Run 21" ~/Sample1_R*.fq \
    --file-type=fastqsanger --dbkey=hg38
