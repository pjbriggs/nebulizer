#!/usr/bin/env python
#
# Manage data libraries in a Galaxy instance
import sys
import optparse
import nebulizer

"""
manage_library.py

"""

__version__ = '0.0.1'

if __name__ == "__main__":
    # Initialise parser with common options
    p = optparse.OptionParser(usage=\
                              "\n\t%prog [options] CMD GALAXY_URL [args...]",
                              version="%%prog %s" % __version__,
                              description="Manage data libraries in the specified "
                              "Galaxy instance.")
    p.add_option('-k','--api_key',action='store',dest='api_key',default=None,
                 help="specify API key for GALAXY_URL (otherwise will try to "
                 "look up from .nebulizer file)")
    p.add_option('-n','--no-verify',action='store_true',dest='no_verify',default=False,
                 help="don't verify HTTPS connections")
    # Get major command and Galaxy URL or alias
    if len(sys.argv) < 3:
        p.error("Need to supply a command and Galaxy URL or alias")
    command = sys.argv[1]
    galaxy_url = sys.argv[2]

    # Populate parser with additional arguments depending on
    # major command
    if command == 'create_library':
        p.add_option('-d','--description',action='store',dest='description',
                     default=None,help="optional description")
        p.add_option('-s','--synopsis',action='store',dest='synopsis',
                     default=None,help="optional synopsis")
    elif command == 'create_folder':
        p.add_option('-d','--description',action='store',dest='description',
                     default=None,help="optional description")
    elif command == 'add_datasets':
        p.add_option('--server',action='store_true',dest='from_server',default=False,
                     help="upload files from Galaxy server file system paths "
                     "(default is to upload files from local system)")
        p.add_option('--link',action='store_true',dest='link',default=False,
                     help="create symlinks to files on server (only valid if used "
                     "with --server; default is to copy files into Galaxy)")
        p.add_option('--dbkey',action='store',dest='dbkey',default='?',
                     help="dbkey to assign to files (default is '?')")
        p.add_option('--file_type',action='store',dest='file_type',default='auto',
                     help="file type to assign to files (default is 'auto')")
        
    # Process remaining arguments on command line
    options,args = p.parse_args(sys.argv[3:])
    api_key = options.api_key
    verify = not options.no_verify
    if not verify:
        sys.stderr.write("WARNING SSL certificate verification has been disabled\n")
        nebulizer.turn_off_urllib3_warnings()

    # Set up Nebulizer instance to interact with Galaxy
    ni = nebulizer.Nebulizer(galaxy_url,api_key,verify=verify)

    # Handle commands
    if command == 'list':
        if len(args) == 1:
            # List folders in data library
            ni.list_library_contents(args[0])
        else:
            # List data libraries
            ni.list_data_libraries()
    elif command == 'create_library':
        # Create a new data library
        if len(args) == 1:
            ni.create_library(args[0],
                              description=options.description,
                              synopsis=options.synopsis)
        else:
            p.error("Usage: create_library NAME")
    elif command == 'create_folder':
        # Create a new folder data library
        if len(args) == 1:
            ni.create_folder(args[0],description=options.description)
        else:
            p.error("Usage: create_folder PATH")
    elif command == 'add_datasets':
        # Add a dataset to a library
        if len(args) != 2:
            p.error("Usage: add_dataset DEST FILE [FILE...]")
        ni.add_library_datasets(args[0],args[1:],
                                from_server=options.from_server,
                                link_only=options.link,
                                file_type=options.file_type,
                                dbkey=options.dbkey)
    else:
        p.error("Unrecognised command: '%s'" % command)
