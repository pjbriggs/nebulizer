============
Installation
============

Virtualenv and pip_
===================

For a traditional installation of Nebulizer, first set up a Python
virtualenv (this example creates a new one in ``.venv``) and then
install with ``pip``:

::

    $ virtualenv .venv;
    $ source .venv/bin/activate
    $ pip install nebulizer

When installed this way, Nebulizer can be upgraded as follows:

::

    $ . .venv/bin/activate
    $ pip install -U nebulizer

To install or update to the latest development branch of Nebulizer
with ``pip``, use the  following ``pip install`` idiom instead:

::

    $ pip install -U git+git://github.com/pjbriggs/nebulizer.git@devel

Nebulizer should work with recent Python 3 versions.

Conda
=====

Nebulizer can be installed using Conda_ (most easily obtained via the
`Miniconda Python distribution <http://conda.pydata.org/miniconda.html>`__):

::

    $ conda config --add channels bioconda
    $ conda install nebulizer

Note that the version available via ``bioconda`` may lag the
most recent version available via ``pip``.

.. _pip: https://pip.pypa.io/
.. _Conda: https://conda.io/
