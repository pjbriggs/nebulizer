#!/usr/bin/env python
#
# nebulizer: Python lib for Galaxy bootstrapping functionality

import sys
import os
import re
import fnmatch
from bioblend import galaxy

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

class Nebulizer:
    """
    Class wrapping functionality from bioblend

    """

    def __init__(self,galaxy_url,api_key=None,verify=True):
        """
        Creat a new Nebulizer instance

        Arguments:
          galaxy_url (str): URL for the Galaxy instance to connect to
          api_key (str): API key to use when accessing Galaxy
          verify (bool): if True then turn off verification of SSL
            certificates for HTTPs connections

        """
        if api_key is None:
            galaxy_url,api_key = Credentials().fetch_key(galaxy_url)
        self._galaxy_url = galaxy_url
        self._gi = galaxy.GalaxyInstance(url=galaxy_url,key=api_key)
        self._gi.verify = verify

    @property
    def galaxy_url(self):
        return self._galaxy_url

    def create_user(self,email,username,passwd):
        """Create a new user account with the specified credentials
        
        """
        try:
            galaxy.users.UserClient(self._gi).create_local_user(username,email,passwd)
            return True
        except galaxy.client.ConnectionError,ex:
            print "Failed to create user:"
            print ex
            return False

    def check_new_user_info(self,email,username):
        """Check if username or login are already in use

        """
        for user in galaxy.users.UserClient(self._gi).get_users():
            if user['email'] == email:
                sys.stderr.write("User with email '%s' already exists\n" % email)
                return False
            elif galaxy.users.UserClient(self._gi).show_user(user['id'])['username'] == username:
                sys.stderr.write("User with name '%s' already exists\n" % username)
                return False
        return True

    def list_data_libraries(self):
        """
        Return list of data libraries

        """
        for lib in galaxy.libraries.LibraryClient(self._gi).get_libraries():
            print "%s\t%s\t%s" % (lib['name'],lib['description'],lib['id'])
            ##print "%s" % lib

    def library_id_from_name(self,library_name):
        """
        Fetch ID for data library from library name

        Arguments:
          library_name (str): name of data library to look up

        Returns:
          str: ID for data library, or None if name not found.

        """
        try:
            return galaxy.libraries.LibraryClient(self._gi).get_libraries(
                name=library_name)[0]['id']
        except IndexError:
            return None

    def folder_id_from_name(self,library_id,folder_name):
        """
        Fetch ID for folder

        Arguments:
          library_id (str): ID for parent data library
          folder_name (str): name of folder to look up

        Returns:
          str: ID for folder, or None if name not found.

        """
        lib_client = galaxy.libraries.LibraryClient(self._gi)
        folder_name = normalise_folder_path(folder_name)
        ##print "Looking for '%s'" % folder_name
        for folder in lib_client.get_folders(library_id):
            ##print "Checking '%s'" % folder['name']
            if folder['name'] == folder_name:
                return folder['id']
        return None

    def list_library_contents(self,path):
        """
        Get contents of folder in data library

        Arguments:
          path (str): path describing a data library or
            a folder in a library

        """
        # Get name and id for parent data library
        #print "Path '%s'" % path
        lib_client = galaxy.libraries.LibraryClient(self._gi)
        library_name,folder_path = split_library_folder_path(path)
        #print "library_name '%s'" % library_name
        library_id = self.library_id_from_name(library_name)
        # Get library contents
        library_contents = lib_client.show_library(library_id,contents=True)
        # Normalise the folder path for matching
        folder_path = normalise_folder_path(folder_path)
        #print "folder_path '%s'" % folder_path
        # Go through the contents of the library
        dataset_client = galaxy.datasets.DatasetClient(self._gi)
        nitems = 0
        for item in library_contents:
            #print "%s" % item
            item_parent,item_name = os.path.split(item['name'])
            #print "-- Parent '%s'" % item_parent
            if fnmatch.fnmatch(item_parent,folder_path):
                nitems += 1
                if item['type'] == 'folder':
                    folder = lib_client.show_folder(library_id,item['id'])
                    print "%s/\t%s\t%s" % (item_name,
                                           folder['description'],
                                           folder['id'])
                else:
                    dataset = dataset_client.show_dataset(item['id'],
                                                          hda_ldda='ldda')
                    #print "%s" % dataset
                    print "%s\t%s\t%s" % (item_name,
                                          dataset['file_size'],
                                          dataset['file_name'])
        if not nitems:
            print "Total 0"

    def create_library(self,name,description=None,synopsis=None):
        """
        Create a new data library

        Arguments:
          name (str): name of the new data library
          description (str): (optional) text to add as the
            description of the new data library
          synopsis (str): (optional) short 'synopsis' text
            to associate with the library

        Returns:
          str: id for data library.

        """
        lib_client = galaxy.libraries.LibraryClient(self._gi)
        if self.library_id_from_name(name):
            print "Target data library already exists"
            return self.library_id_from_name(name)['id']
        library = lib_client.create_library(name,
                                            description=description,
                                            synopsis=synopsis)
        #print "%s" % library
        return library['id']

    def create_folder(self,path,description=None):
        """
        Create a new folder in a data library

        Arguments:
          path (str): path to the new folder (must be within
            an existing data library)
          description (str): text to add as the description
            of the new folder

        Returns:
          str: id for new folder.

        """
        # Break up the path
        library_name,folder_path = split_library_folder_path(path)
        # Get name and id for parent data library
        lib_client = galaxy.libraries.LibraryClient(self._gi)
        library_id = self.library_id_from_name(library_name)
        #print "library_name '%s'" % library_name
        # Get folder name and base folder
        folder_base,folder_name = os.path.split(folder_path)
        # Check folder with same name doesn't already exist
        folder_id = self.folder_id_from_name(library_id,folder_path)
        #print "folder_id '%s' for '%s'" % (folder_id,folder_path)
        if self.folder_id_from_name(library_id,folder_path):
            print "Target folder already exists"
            return None
        #print "folder_name '%s' folder_base '%s'" % (folder_name,
        #                                             folder_base)
        base_folder_id = self.folder_id_from_name(library_id,folder_base)
        #print "base_folder_id %s" % base_folder_id
        new_folder = lib_client.create_folder(library_id,folder_name,
                                              description=description,
                                              base_folder_id=base_folder_id)
        #print "%s" % new_folder
        return new_folder[0]['id']

    def add_library_datasets(self,path,files,
                             from_server=False,
                             link_only=False,
                             file_type='auto',
                             dbkey='?'):
        """
        Add datasets to a data library

        Arguments:
          path (str): path of folder to add datasets to
          files (list): list of files to upload to the data
            library
          from_server (bool): set True if files to be added are
            on the Galaxy server filesystem (default is False
            i.e. files on the local file system)
          link_only (bool): for files on the Galaxy server
            filesystem, set True to create links to the files
            (default is False i.e. copy files into Galaxy)
          file_type (str): explicit Galaxy file type to apply
            to all uploaded files (default is 'auto')
          dbkey (str): explicit dbkey to apply to all uploaded
            files (default is '?')

        """
        # Break up the path
        library_name,folder_path = split_library_folder_path(path)
        # Get name and id for parent data library
        lib_client = galaxy.libraries.LibraryClient(self._gi)
        library_id = self.library_id_from_name(library_name)
        print "Library name '%s' id '%s'" % (library_name,library_id)
        # Get id for parent folder
        folder_id = self.folder_id_from_name(library_id,folder_path)
        print "Folder name '%s' id '%s'" % (folder_path,folder_id)
        if from_server:
            # Assume that files are on Galaxy fileserver not localhost
            filesystem_paths = '\n'.join(files)
            print "Uploading files from Galaxy server:"
            print "%s" % filesystem_paths
            lib_client.upload_from_galaxy_filesystem(
                library_id,filesystem_paths,
                folder_id=folder_id,
                file_type=file_type,
                dbkey=dbkey,
                link_data_only=link_only,
                roles='')
        else:
            # Files are on localhost
            for f in files:
                print "Uploading file '%s'" % f
                lib_client.upload_file_from_local_path(
                    library_id,f,
                    folder_id=folder_id,
                    file_type=file_type,
                    dbkey=dbkey)

def check_username_format(username):
    """Check that format of 'username' is valid

    """
    return bool(re.match("^[a-z0-9\-]+$",username))

def get_username_from_login(email):
    """Create a public user name from an email address

    """
    return str(email).split('@')[0].lower().replace('.','-').replace('_','-')

def validate_password(passwd):
    """Check if password format is valid

    """
    if len(passwd) < 6:
        return False
    return True

def split_library_folder_path(path):
    """
    Split library path into library and folder components

    Arguments:
      path (str): path describing a folder in a data library

    Returns:
      Tuple: (library_name,folder_name)

    """
    components = path.split('/')
    library_name = components[0]
    if len(components) == 1:
        folder_name = ''
    else:
        folder_name = '/'.join(components[1:])
    return (library_name,folder_name)

def normalise_folder_path(path):
    """
    Normalise a folder path

    Normalise folder paths so that they are always of the
    form

    /path/to/folder

    i.e a single leading slash with no trailing slash

    Arguments:
      path (str): path for a data library folder

    Returns:
      str: normalised folder path.

    """
    return '/'+path.strip('/')

def turn_off_urllib3_warnings():
    """Turn off the warnings from urllib3

    Use this to suppress warnings (e.g. about unverified HTTPS
    certificates) that would otherwise be written out for each
    request in bioblend.

    """
    import requests
    requests.packages.urllib3.disable_warnings()
