#!/usr/bin/env python
#
# bootstrap: utilities for making Galaxy instances for test etc
import sys
import os
import tempfile
import subprocess
import shutil
import ConfigParser
import logging
import time
import random
import string
import socket
import bioblend
import urllib2
import nebulizer
import nebulizer.core as core
import nebulizer.tools as tools
import nebulizer.users as users
import nebulizer.libraries as libraries

logger = logging.getLogger(__name__)

class Git(object):
    """
    Class providing static methods to perform git operations
    """
    @staticmethod
    def clone(repository,target=None,bare=False,cwd=None,
              ignore_existing=False):
        """
        Clone a repository
        """
        if target is None:
            target = os.path.basename(repository)
            if target.endswith(".git"):
                target = target[:-4]
        if cwd is not None:
            target = os.path.join(cwd,target)
        target = os.path.abspath(target)
        if os.path.exists(target) and os.listdir(target):
            logging.warn("Dir exists and is not empty")
            if ignore_existing:
                return target
        git_clone = ['git','clone',repository,target]
        if bare:
            git_clone.append('--bare')
        print git_clone
        status = subprocess.call(git_clone,
                                 cwd=cwd)
        if status != 0:
            raise Exception("Failed to clone repository: '%s'"
                            % repository)
        return target

    @staticmethod
    def checkout(dirn,branch):
        """
        Checkout a branch
        """
        dirn = os.path.abspath(dirn)
        git_checkout = ['git','checkout',branch]
        print git_checkout
        status = subprocess.call(git_checkout,cwd=dirn)
        if status != 0:
            raise Exception("Failed to checkout branch: '%s'"
                            % branch)

    @staticmethod
    def pull(dirn,remote=None,branch=None,ff_only=False):
        """
        Pull in changes from remote
        """
        dirn = os.path.abspath(dirn)
        git_pull = ['git','pull']
        if ff_only:
            git_pull.append('--ff-only')
        if remote is not None:
            git_pull.append(remote)
        if branch is not None:
            git_pull.append(branch)
        print git_pull
        status = subprocess.call(git_pull,cwd=dirn)
        if status != 0:
            raise Exception("Failed to pull in changes from remote")

class GalaxyInstance(object):
    """
    Base class for creating and managing local Galaxy services


    By default this will create a local Galaxy server. Minimal
    usage example:

    >>> g = GalaxyInstance()
    >>> g.start()

    Processes should then be able to communicate with the server.
    To get the name (e.g. http://127.0.0.1:8080):

    >>> g.server

    To get the master API key:

    >>> g.master_api_key

    To check it's running:

    >>> g.is_running # True if server is running

    To reset to "factory" state:

    >>> g.reset()

    To stop running server:

    >>> g.stop()

    Note that if a port is not specified then a random port
    will be used, which will be different each time the server
    is started.
    """
    def __init__(self,name="Galaxy",database="universe.sqlite",
                 config_file="galaxy.ini",run_sh="run.sh",
                 log_file="paster.log",parent_dir=None,
                 port=None,admin_users=None,master_api_key=None,
                 repository="https://github.com/galaxyproject/galaxy.git",
                 release="release_17.05",
                 import_db=None):
        """
        Create a GalaxyInstance object
        """
        # Define the core components
        self.name = name
        self.database = database       # community.sqlite for toolshed
        self.config_file = config_file # tool_shed.ini for toolshed
        self.run_sh = run_sh           # run_tool_shed.sh for toolshed
        self.log_file = log_file       # tool_shed_webapp.log for toolshed
        self.import_db = import_db
        self.assets = ['database/%s' % self.database,
                       'database/dependencies',
                       'config/tool_conf.xml',
                       '../shed_tools']
        # Galaxy state
        self.is_running = False
        # Host and port
        # Actual port is set on startup
        self.host = "127.0.0.1"
        self.requested_port = port
        self.port = None
        # Admin users
        if admin_users is None:
            admin_users = ""
        self.admin_users = admin_users.split(',')
        # Generate master API key if none supplied
        if master_api_key is None:
            master_api_key = self.get_random_string()
        self.master_api_key = master_api_key
        # Git repository and branch
        self.galaxy_repo = repository
        self.galaxy_release = release
        # Parent directory
        if parent_dir is None:
            parent_dir = tempfile.mkdtemp(dir=os.getcwd())
        self.parent_dir = os.path.abspath(parent_dir)
        if not os.path.exists(self.parent_dir):
            os.mkdir(self.parent_dir)
        self.fetch_galaxy_source()
        # Make the config file
        self.galaxy_config_file = os.path.join(self.galaxy_dir,
                                               "config",
                                               self.config_file)
        sample_galaxy_config = self.galaxy_config_file + ".sample"
        config = dict()
        config['server:main'] = { 'port': self.port,
                                  'host': self.host }
        config['app:main'] = { 'database_connection':
                               "sqlite:///./database/%s?isolation_level=IMMEDIATE" % self.database, 
                               'master_api_key': self.master_api_key,
                               'admin_users': ','.join(self.admin_users)
        }
        self.make_config(sample_galaxy_config,
                         self.galaxy_config_file,
                         **config)

    def fetch_galaxy_source(self):
        """
        Fetch/clone the Galaxy source code
        """
        # Clone Galaxy into parent dir
        self.galaxy_dir = os.path.join(self.parent_dir,"galaxy")
        Git.clone(self.galaxy_repo,self.galaxy_dir,
                  ignore_existing=True)
        # Switch to the correct version
        Git.checkout(self.galaxy_dir,self.galaxy_release)
        Git.pull(self.galaxy_dir,
                 remote="origin",
                 branch=self.galaxy_release,
                 ff_only=True)
        
    @property
    def server(self):
        """
        Return server name e.g. "http://127.0.0.1:8080"
        """
        return "http://%s:%s" % (self.host,self.port)

    @property
    def galaxy_log(self):
        """
        Return log file for Galaxy instance
        """
        return os.path.join(self.galaxy_dir,self.log_file)

    def get_port(self):
        """
        Return a random unused port
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('localhost', 0))
        addr,port = s.getsockname()
        s.close()
        return port
    
    def get_random_string(self,n=32):
        """
        Return a random string of characters
        """
        chars = string.ascii_uppercase + string.ascii_lowercase
        return ''.join(random.choice(chars) for _ in range(n))

    def make_config(self,sample,config_file,**kws):
        """
        Create a galaxy config file
        """
        config = ConfigParser.ConfigParser()
        config.read(sample)
        for section in kws:
            for key in kws[section]:
                value = kws[section][key]
                if value is None:
                    continue
                print "Setting [%s]:%s = %s" % (section,
                                                key,
                                                value)
                config.set(section,key,value)
        with open(config_file,'w') as fp:
            config.write(fp)
            
    def start(self,timeout=60):
        """
        Start Galaxy instance running
        """
        poll_interval = 5
        if self.is_running:
            print "Already running"
            return
        # Run Galaxy's setup script
        print "Running common_startup.sh"
        subprocess.call(['./scripts/common_startup.sh'],
                        cwd=self.galaxy_dir)
        # Deal with database
        if self.import_db is not None and \
           not os.path.exists("database/%s" % self.database):
            # Import SQLite database file
            print "Copying %s to %s" % (self.import_db,self.database)
            shutil.copy(self.import_db,
                        os.path.join(self.galaxy_dir,
                                     'database',
                                     self.database))
            print "Migrating database"
            subprocess.call(['sh','manage_db.sh','upgrade'],
                            cwd=self.galaxy_dir)
        # Set the port
        if self.requested_port is not None:
            self.port = self.requested_port
        else:
            print "Acquiring free port"
            self.port = self.get_port()
        print "Updating port in %s" % self.config_file
        config = ConfigParser.ConfigParser()
        config.read(self.galaxy_config_file)
        config.set("server:main","port",self.port)
        with open(self.galaxy_config_file,'w') as fp:
            config.write(fp)
        print "Starting %s: %s" % (self.name,self.server)
        if os.path.exists(self.galaxy_log):
            print "Removing old log file"
            os.remove(self.galaxy_log)
        subprocess.call(['sh',self.run_sh,'--daemon'],
                        cwd=self.galaxy_dir)
        sys.stdout.write("Wait for %s to come up: " % self.name)
        ntries = 0
        while (ntries*poll_interval) < timeout:
            if os.path.exists(self.galaxy_log):
                with open(self.galaxy_log,'r') as log:
                    contents = log.read()
                    if contents.find("Removing PID file") > -1:
                        sys.stdout.write("\n")
                        raise Exception("Failed to start %s" % self.name)
                    if contents.find("serving on %s" % self.server) > -1:
                        self.is_running = True
                        break
            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(poll_interval)
        if not self.is_running:
            sys.stdout.write("timed out\n" % self.name)
            raise Exception("Timed out waiting to start %s" % self.name)
        else:
            sys.stdout.write("\n%s ready: %s\n" % (self.name,self.server))

    def stop(self):
        """
        Stop running Galaxy instance
        """
        if not self.is_running:
            print "Not running"
            return
        print "Stopping %s" % self.name
        subprocess.call(['sh',self.run_sh,'--stop-daemon'],
                        cwd=self.galaxy_dir)
        if os.path.exists(self.galaxy_log):
            print "Removing log file"
            os.remove(self.galaxy_log)
        self.is_running = False

    def reset(self,keep_virtual_env=False):
        """
        Attempt to restore to pristine state
        """
        restart = False
        if self.is_running:
            self.stop()
            restart = True
        removal_list = [x for x in self.assets]
        if not keep_virtual_env:
            removal_list.append('.venv')
        for item in removal_list:
            item = os.path.join(self.galaxy_dir,item)
            if os.path.exists(item):
                print "Removing %s" % item
                if os.path.isdir(item):
                    shutil.rmtree(item)
                else:
                    os.remove(item)
        self.port = None
        if restart:
            self.start()

class GalaxyServer(GalaxyInstance):
    """
    Create and manage local Galaxy server
    """
    def __init__(self,**kws):
        kws['name'] = "Galaxy"
        kws['database'] = "universe.sqlite"
        kws['config_file'] = "galaxy.ini"
        kws['run_sh'] = "run.sh"
        kws['log_file'] = "paster.log"
        ##if 'port' not in kws:
        ##    kws['port'] = 8080
        GalaxyInstance.__init__(self,**kws)
    def galaxy_instance(self):
        """
        Return bioblend GalaxyInstance object
        """
        if not self.is_running:
            raise Exception("%s: not running" % self.name)
        return bioblend.galaxy.GalaxyInstance(
            url=self.server,
            key=self.master_api_key)
        
    def add_user(self,email,name,passwd):
        """
        Create a user within the Galaxy instance
        """
        if not self.is_running:
            raise Exception("%s: not running" % self.name)
        gi = self.galaxy_instance()
        bioblend.galaxy.users.UserClient(gi).create_local_user(name,
                                                               email,
                                                               passwd)

class GalaxyToolshed(GalaxyInstance):
    """
    Create and manage local Toolshed server

    NB this is largely untried
    """
    def __init__(self,**kws):
        kws['name'] = "Toolshed"
        kws['database'] = "community.sqlite"
        kws['config_file'] = "tool_shed.ini"
        kws['run_sh'] = "run_tool_shed.sh"
        kws['log_file'] = "tool_shed_webapp.log"
        if 'port' not in kws:
            kws['port'] = 9090
        GalaxyInstance.__init__(self,**kws)

# Main program

if __name__ == "__main__":
    # Clone bare repository for cache
    Git.clone("https://github.com/galaxyproject/galaxy.git",
              "galaxy.git",
              bare=True,ignore_existing=True)
    # Fetch bootstrap database
    if not os.path.exists("db_galaxy_rev_0120.sqlite"):
        with open("db_galaxy_rev_0120.sqlite","wb") as fp:
            fp.write(urllib2.urlopen("https://github.com/fls-bioinformatics-core/galaxy-tools/blob/master/testing/db_galaxy_rev_0120.sqlite?raw=true").read())
    # Create a Galaxy instance for testing
    galaxy = GalaxyServer(parent_dir="nebulizer_test",
                          repository="galaxy.git",
                          release="release_17.05",
                          import_db="db_galaxy_rev_0120.sqlite",
                          admin_users="admin@localhost.org")
    try:
        # Start the test instance
        galaxy.start()
        # Get an instance to work with
        ## NB can generate ugly messages when using
        ## master API key
        gi = core.get_galaxy_instance(
            galaxy.server,
            api_key=galaxy.master_api_key)
        # Core functions
        core.get_galaxy_config(gi)
        core.get_current_user(gi)
        core.ping_galaxy_instance(gi)
        # User creation etc
        users.list_users(gi)
        ## NB create_user will fail if username is not
        ## specified even though documentation says this
        ## isn't required
        users.create_user(gi,"peter.briggs@manchester.ac.uk",
                          passwd="9@55w0rd")
        # Try again with username specified
        users.create_user(gi,"peter.briggs@manchester.ac.uk",
                          username="pjbriggs",
                          passwd="9@55w0rd")
        users.list_users(gi)
        # Reset to clear data etc
        galaxy.reset(keep_virtual_env=True)
        gi = galaxy.galaxy_instance()
        users.list_users(gi)
        # Tool installation
        tools.list_installed_repositories(gi)
        tools.install_tool(gi,
                           "toolshed.g2.bx.psu.edu",
                           "trimmomatic",
                           "pjbriggs",
                           revision="6eeacf19a38e")
        tools.list_installed_repositories(gi)
        tools.update_tool(gi,
                          "toolshed.g2.bx.psu.edu",
                          "trimmomatic",
                          "pjbriggs")
        tools.list_installed_repositories(gi)
        # Reset to clear data etc
        galaxy.reset(keep_virtual_env=True)
        gi = galaxy.galaxy_instance()
        # Data libraries
        galaxy.add_user("admin@localhost.org",
                        "admin",
                        "galaxyadmin")
        users.list_users(gi)
        libraries.list_data_libraries(gi)
        libraries.create_library(gi,
                                 "My library")
        libraries.list_data_libraries(gi)
        libraries.add_library_datasets(gi,
                                       "My library",
                                       ["/home/pjb/BCF_Work/test-data/fastqs/Illumina_SG_R1.fastq",])
        libraries.list_library_contents(gi,"My library")
        admin_gi = core.get_galaxy_instance(
            galaxy.server,
            email="admin@localhost.org",
            password="galaxyadmin")
        libraries.add_library_datasets(admin_gi,
                                       "My library/",
                                       ["/home/pjb/BCF_Work/test-data/fastqs/Illumina_SG_R1.fastq",])
        libraries.list_library_contents(gi,"My library")
    except Exception as ex:
        print "Failed: %s" % ex
    galaxy.stop()
