#!/usr/bin/env python
#
# core: core nebulizer classes and functions

import sys
import os
import re
import fnmatch
from bioblend import galaxy
from bioblend.galaxy.client import ConnectionError

class Credentials:
    """Class for managing credentials for Galaxy instances

    Credentials for different galaxy instances can be
    stored in a file under $HOME/.nebulizer

    Entries in the file consist of lines with three tab
    separated values:

    ALIAS   URL    API_KEY

    Blank lines or lines starting '#' are skipped.

    """

    def __init__(self):
        self._key_file = os.path.join(os.path.expanduser("~"),
                                           '.nebulizer')

    def store_key(self,name,url,api_key):
        """Store a Galaxy API key

        Appends an entry to the key file.

        """
        with open(self._key_file,'w+') as fp:
            fp.write("%s\t%s\t%s\n" % (name,url,api_key))

    def fetch_key(self,name):
        """Fetch credentials associated with a Galaxy instance

        Looks up the credentials associated with the
        alias 'name', and returns the tuple:

        (GALAXY_URL,API_KEY)

        Raises a KeyError if no matching alias is found.

        """
        if os.path.exists(self._key_file):
            with open(self._key_file,'r') as fp:
                for line in fp:
                    if line.startswith('#') or not line.strip():
                        continue
                    alias,url,api_key = line.strip().split('\t')
                    if alias == name:
                        return (url,api_key)
        raise KeyError("'%s': not found" % name)

def get_galaxy_instance(galaxy_url,api_key=None,verify=True):
    """
    Return Bioblend GalaxyInstance

    Arguments:
      galaxy_url (str): URL for the Galaxy instance to connect to
      api_key (str): API key to use when accessing Galaxy
      verify (bool): if True then turn off verification of SSL
        certificates for HTTPs connections

    """
    if api_key is None:
        galaxy_url,api_key = Credentials().fetch_key(galaxy_url)
    print "Connecting to %s" % galaxy_url
    gi = galaxy.GalaxyInstance(url=galaxy_url,key=api_key)
    gi.verify = verify
    user = galaxy.users.UserClient(gi).get_current_user()
    print "Username %s" % user['email']
    return gi

def turn_off_urllib3_warnings():
    """
    Turn off the warnings from urllib3

    Use this to suppress warnings (e.g. about unverified HTTPS
    certificates) that would otherwise be written out for each
    request in bioblend.

    """
    import requests
    requests.packages.urllib3.disable_warnings()
