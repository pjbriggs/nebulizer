#!/bin/bash
#
# Functions for setting up and managing Galaxy instance for testing
#
function setup_galaxy() {
    # Args:
    # 1: Galaxy version (=branch/tag name)
    #
    # Initialise
    local galaxy_version=$1
    # Clone Galaxy
    if [ ! -d galaxy ] ; then
	echo -n Cloning Galaxy...
	git clone -b $galaxy_version https://github.com/galaxyproject/galaxy.git
	echo done
    fi
    # Clean up any existing configuration or data
    if [ -f galaxy/config/galaxy.ini ] ; then
	echo -n Removing existing galaxy.ini...
	/bin/rm -f galaxy/config/galaxy.ini
	echo done
    fi
    if [ -d shed_tools ] ; then
	echo -n Removing existing shed_tools dir...
	/bin/rm -rf shed_tools
	echo done
    fi
    if [ -f galaxy/database/universe.sqlite ] ; then
	echo -n Removing existing universe.sqlite...
	/bin/rm -f galaxy/database/universe.sqlite
	echo done
    fi
    if [ -d galaxy/database/dependencies ] ; then
	echo -n Removing existing dependencies dir...
	/bin/rm -rf galaxy/database/dependencies
	echo done
    fi
    # Make a galaxy.ini file
    local galaxy_config_file=$(pwd)/galaxy.ini
    echo Setting up $galaxy_config_file
    cp galaxy/config/galaxy.ini.sample $galaxy_config_file
    echo Setting master API key
    sed -i 's,#master_api_key = .*,master_api_key = '$(pwgen 64 1)',g' $galaxy_config_file
    echo Setting tool_dependency_dir
    sed -i 's,#tool_dependency_dir = .*,tool_dependency_dir = tool_dependencies,g' $galaxy_config_file
}
#
#
function get_config_value() {
    local galaxy_config_file=$(pwd)/galaxy.ini
    if [ ! -f $galaxy_config_file ] ; then
	return
    fi
    grep "^${1}" $galaxy_config_file | cut -d= -f2
}
#
#
function start_galaxy() {
    if [ -f galaxy/paster.log ] ; then
	/bin/rm -f galaxy/paster.log
    fi
    export GALAXY_CONFIG_FILE=$(pwd)/galaxy.ini
    echo Using config file at $GALAXY_CONFIG_FILE
    sh galaxy/run.sh --daemon
    echo -n Waiting for Galaxy to come up
    while [ -z "$(grep '^Starting server' galaxy/paster.log)" ] ; do
	echo -n .
	sleep 5
    done
    echo ok
}
#
#
function stop_galaxy() {
    echo -n Stopping Galaxy...
    sh galaxy/run.sh --stop-daemon
    echo done
}
