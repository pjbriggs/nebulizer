===============
General options
===============

Nebulizer supports a number of general options for managing
how connections are made to Galaxy servers, how to authenticate,
and what information to output.

-----------------------------------------
Authenticating without stored credentials
-----------------------------------------

Use ``--api_key`` (``-k``) to explicitly specify the API key to
use for authentication on the command line, e.g.

::

   nebulizer -k API_KEY COMMAND...

Use the ``--username`` (``-u``) option to authenticate using the
normal Galaxy login credentials (i.e. email and password)
instead of the API key, e.g.

::

   nebulizer -u USER@DOMAIN COMMAND...

You will be prompted to enter the password, but you can also use
the ``--galaxy_password`` (``-P``) option to specify it explicitly
on the command line.

-----------------------------------------
Controlling warnings and debugging output
-----------------------------------------

``--suppress-warnings`` (``-q``) suppresses warning messages from
Nebulizer; conversely debugging output can be enabled using the
``--debug`` option.

----------------------------------------------
Handling SSL certificate verification failures
----------------------------------------------

Nebulizer commands will fail for Galaxy instances which are served over
``https`` protocol without a valid SSL certificate, reporting an error like::

  [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:590), 0 attempts left: None

In this case adding the ``--no-verify`` (``-n``) option turns off the
certificate verification and should enable a connection to be made.
