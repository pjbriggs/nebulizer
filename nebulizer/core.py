#!/usr/bin/env python
#
# core: core nebulizer classes and functions

import sys
import os
import re
import fnmatch
import logging
import time
from bioblend import galaxy
from bioblend.galaxy.client import ConnectionError

logger = logging.getLogger(__name__)

class Credentials:
    """Class for managing credentials for Galaxy instances

    Credentials for different galaxy instances can be
    stored in a file under $HOME/.nebulizer

    Entries in the file consist of lines with three tab
    separated values:

    ALIAS   URL    API_KEY

    Blank lines or lines starting '#' are skipped.

    """

    def __init__(self,key_file=None):
        """
        Create a new Credentials instance

        Arguments:
          key_file (str): if supplied then should specify
            the path to the credentials file (defaults to
            $HOME/.nebulizer)

        """
        if key_file is None:
            key_file = os.path.join(os.path.expanduser("~"),
                                    '.nebulizer')
        self._key_file = os.path.abspath(key_file)

    def list_keys(self):
        """
        List aliases for API keys stored in credentials file

        Returns:
          List: list of aliases.

        """
        key_names = []
        if os.path.exists(self._key_file):
            with open(self._key_file) as fp:
                for line in fp:
                    if line.startswith('#') or not line.strip():
                        continue
                    key_names.append(line.strip().split('\t')[0])
        return key_names

    def store_key(self,name,url,api_key):
        """
        Store a Galaxy API key

        Appends an entry to the key file.

        Arguments:
          name (str): alias to store the key against
          url (str): URL of the Galaxy instance
          api_key (str): API key for the Galaxy instance

        Returns:
          Boolean: True if key was updated, False on error.
        """
        if not api_key:
            logger.warning("Empty API key")
            return False
        with open(self._key_file,'a') as fp:
            fp.write(f"{name}\t{url}\t{api_key}\n")
        return True

    def remove_key(self,name):
        """
        Remove a Galaxy API key

        Removes a key entry from the key file.

        Arguments:
          name (str) alias of the key to be removed

        Returns:
          Boolean: True if key was removed, False on error.
        """
        key_names = self.list_keys()
        if name not in key_names:
            logger.error("'%s': not found" % name)
            return False
        # Store the keys
        cached_keys = {
            name: list(self.fetch_key(name))
            for name in key_names
        }
        # Wipe the key file
        with open(self._key_file,'w') as fp:
            fp.write("#.nebulizer\n#Aliases\tGalaxy URL\tAPI key\n")
        # Store the cached keys again
        for alias in key_names:
            if name != alias:
                url,api_key = cached_keys[alias]
                self.store_key(alias,url,api_key)
        return True

    def update_key(self,name,new_url=None,new_api_key=None):
        """
        Update a Galaxy API key

        Updates the stored information in the key file.

        Arguments:
          name (str): alias of the key entry to be updated
          new_url (str): optional, new URL for the Galaxy
            instance
          new_api_key (str): optional, new API key for the
            Galaxy instance

        Returns:
          Boolean: True if key was updated, False on error.
        """
        try:
            url,api_key = self.fetch_key(name)
        except KeyError:
            logger.error("'%s': not found" % name)
            return False
        if new_url:
            url = new_url
        if new_api_key:
            api_key = new_api_key
        self.remove_key(name)
        self.store_key(name,url,api_key)
        return True

    def fetch_key(self,name):
        """
        Fetch credentials associated with a Galaxy instance

        Returns the credentials (i.e. Galaxy URL and API key)
        associated with the specified alias

        Raises a KeyError if no entry matching the alias is
        found.

        Arguments:
          name (str): alias of the key entry to fetch

        Returns:
          Tuple: consisting of (GALAXY_URL,API_KEY)
        """
        if os.path.exists(self._key_file):
            with open(self._key_file) as fp:
                for line in fp:
                    if line.startswith('#') or not line.strip():
                        continue
                    alias,url,api_key = line.strip().split('\t')
                    if alias == name or url == name:
                        return (url,api_key)
        raise KeyError("'%s': not found" % name)

    def has_key(self,name):
        """
        Check if alias exists
        """
        try:
            self.fetch_key(name)
            return True
        except KeyError:
            return False

class Reporter:
    """
    Class for reporting column data

    Given multiple "lines" of column data (supplied
    as lists), pretty print the data in columns.

    Example usage:

    >>> output = Reporter()
    >>> output.append(['Some data',1.0,3])
    >>> output.append(['More stuff',21.9,19])
    >>> output.report()
    Some data   1.0   3
    More stuff  21.9  19
    """
    def __init__(self):
        """
        New Reporter instance
        """
        self._content = list()
        self._field_widths = list()
    def append(self,line):
        """
        Add a line of data

        Arguments:
          line (list): list of data items to
            append
        """
        self._content.append(line)
        for ix,item in enumerate(line):
            try:
                self._field_widths[ix] = max(self._field_widths[ix],
                                            len(str(item)))
            except IndexError:
                self._field_widths.append(len(str(item)))
    @property
    def nlines(self):
        """
        Number of lines stored
        """
        return len(self._content)
    def report(self,delimiter=None,padding=True,prefix=None,
               rstrip=True):
        """
        Pretty-print the data

        Arguments:
          delimiter (str): delimiter to use (defaults
            to two space characters i.e. '  ')
          padding (bool): if True then line up columns
            of data by padding with spaces
          prefix (str): string to prepend to each line
          rstrip (bool): if True then strip all trailing
            whitespace from lines
        """
        output = []
        if delimiter is None:
            delimiter = '  '
        if padding:
            for line in self._content:
                # Apply padding to all but the last field
                out_line = ["%-*s" % (width,str(item))
                               for width,item
                               in zip(self._field_widths[:-1],
                                      line[:-1])]
                # Add the final field with no padding
                out_line.append(str(line[-1]))
                output.append(out_line)
        else:
            for line in self._content:
                output.append([str(item) for item in line])
        if not prefix:
            prefix = ''
        for line in output:
            out_line = "{}{}".format(prefix,delimiter.join(line))
            if rstrip:
                out_line = out_line.rstrip()
            print(out_line)

def get_galaxy_instance(galaxy_url,api_key=None,email=None,password=None,
                        verify_ssl=True,validate_key=True):
    """
    Return Bioblend GalaxyInstance

    Attempts to connect to the specified Galaxy instance and
    verify that the connection is working by requesting the
    config for that instance.

    Arguments:
      galaxy_url (str): URL for the Galaxy instance to connect to
      api_key (str): API key to use when accessing Galaxy
      email (str): Galaxy e-mail address corresponding to the user
        (alternative to api_key; also need to supply a password)
      password (str): password of Galaxy account corresponding to
        email address (alternative to api_key)
      verify_ssl (bool): if True then turn off verification of SSL
        certificates for HTTPs connections

    Returns:
      GalaxyInstance: a bioblend GalaxyInstance for the connection,
        or None if the connection failed or couldn't be verified.

    """
    try:
        galaxy_url,stored_key = Credentials().fetch_key(galaxy_url)
    except KeyError as ex:
        logger.debug("Failed to find credentials for %s" %
                     galaxy_url)
        stored_key = None
    if api_key is None:
        api_key = stored_key
    logger.debug("Connecting to %s" % galaxy_url)
    if not validate_key:
        gi = galaxy.GalaxyInstance(url=galaxy_url)
    elif email is not None:
        gi = galaxy.GalaxyInstance(url=galaxy_url,email=email,
                                   password=password)
    else:
        gi = galaxy.GalaxyInstance(url=galaxy_url,key=api_key)
    gi.verify = verify_ssl
    if not get_galaxy_config(gi):
        return None
    user = get_current_user(gi)
    if user is not None:
        logger.debug("Connected as user %s" % user['email'])
    else:
        logger.debug("Unable to determine associated user")
    return gi

def get_galaxy_config(gi):
    """
    Requests configuration data for a Galaxy instance

    Arguments:
      gi (bioblend.galaxy.GalaxyInstance): Galaxy instance

    Returns:
      Dictionary: the configuration data for the Galaxy
        instance (will be empty if this couldn't be
        retrieved)
    """
    try:
        return galaxy.config.ConfigClient(gi).get_config()
    except ConnectionError as ex:
        print(ex)
        return {}

def get_current_user(gi):
    """
    Requests data on the user for an API connection

    Arguments:
      gi (bioblend.galaxy.GalaxyInstance): Galaxy instance

    Returns:
      Dictionary: the data on the user, or 'None' if the user
        couldn't be determined.
    """
    try:
        return galaxy.users.UserClient(gi).get_current_user()
    except ConnectionError:
        return None

def ping_galaxy_instance(gi):
    """
    Send a request to a Galaxy instance and report result

    Arguments:
      gi (bioblend.galaxy.GalaxyInstance): Galaxy instance

    Returns:
      Tuple: a tuple of the form (retcode,time). 'retcode'
        will be zero if the response from the server was okay,
        otherwise it is set to the status code of the failed
        response. 'time' is the time taken for the request to
        be sent and the response to be received, in seconds.

    """
    # Make a request
    try:
        start = time.time()
        galaxy.config.ConfigClient(gi).get_config()
        retcode = 0
    except ConnectionError as ex:
        retcode = ex.status_code
    end = time.time()
    return (retcode,end-start)

def prompt_for_confirmation(question,default=None):
    """
    Prompt the user to confirm an action

    Arguments:
      question: text to display next to the prompt
      default: default to use if user doesn't supply
        an explicit response (one of 'y','yes','n'
        or 'no')

    Returns:
      True if user confirms, False if not.

    """
    responses = {
        'yes': True,
        'ye' : True,
        'y'  : True,
        'no' : False,
        'n'  : False,
    }
    if default is None:
        prompt = " [y/n] "
    elif default.lower().startswith('y'):
        prompt = " [Y/n] "
    elif default.lower().startswith('n'):
        prompt = " [y/N] "
    else:
        raise Exception("Invalid default for prompt: %s" %
                        default)
    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return responses[default.lower()]
        elif choice in responses:
            return responses[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

def turn_off_urllib3_warnings():
    """
    Turn off the warnings from urllib3

    Use this to suppress warnings (e.g. about unverified HTTPS
    certificates) that would otherwise be written out for each
    request in bioblend.

    """
    import requests
    requests.packages.urllib3.disable_warnings()
