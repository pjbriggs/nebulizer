#!/usr/bin/env python

import sys
import optparse
from bioblend import galaxy

if __name__ == '__main__':
    # Collect arguments
    p = optparse.OptionParser(usage="%prog GALAXY_URL API_KEY TOOLSHED NAME REVISION OWNER",
                              description="Install a tool into the specified Galaxy instance "
                              "from the specified toolshed")
    options,args = p.parse_args()
    if len(args) != 6:
        p.error("Wrong arguments")
    galaxy_url = args[0]
    api_key = args[1]
    toolshed = args[2]
    name = args[3]
    rev = args[4]
    owner = args[5]

    print "Install tool into Galaxy instance at %s" % galaxy_url
    print "Toolshed : %s" % toolshed
    print "name     : %s" % name
    print "Revision : %s" % rev
    print "Owner    : %s" % owner

    gi = galaxy.GalaxyInstance(url=galaxy_url,key=api_key)
    tc = galaxy.tools.ToolClient(gi)
    tcs = galaxy.toolshed.ToolShedClient(gi)

    try:
        tcs.install_repository_revision(toolshed,name,owner,rev,
                                        install_tool_dependencies=True,
                                        install_repository_dependencies=True,
                                        tool_panel_section_id=None,
                                        new_tool_panel_section_label="Shed Tools")
    except galaxy.client.ConnectionError,ex:
        print "Failed to install tool:"
        print ex
        sys.exit(1)
    print "Done"
        

