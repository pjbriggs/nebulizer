#!/bin/bash
#
# This is a script to run a set of simple tests against the
# nebulizer command line (cli).
#
# Start up
echo =================
echo Testing Nebulizer
echo =================
#
# Import external functions
. $(dirname $0)/galaxy.sh
. $(dirname $0)/test.framework.sh
. $(dirname $0)/test.cases.sh
#
# Initialise variables
GALAXY_VERSION=
BIOBLEND_VERSION=0.8.0
NEBULIZER_PKG=nebulizer
NEBULIZER_OPTS=-n
#
# Collect command line
function usage() {
    echo "Usage: $(basename $0) GALAXY_VERSION [NEBULIZER_PKG]"
}
if [ -z "$1" ] ; then
    usage
    exit 1
fi
GALAXY_VERSION=$1
if [ ! -z "$2" ] ; then
    NEBULIZER_PKG=$2
fi
#
# Report settings
echo Galaxy version: $GALAXY_VERSION
echo Bioblend version: $BIOBLEND_VERSION
echo Nebulizer package: $NEBULIZER_PKG
echo Nebulizer options: $NEBULIZER_OPTS
#
# Create directory and log file
if [ ! -d $GALAXY_VERSION ] ; then
    mkdir $GALAXY_VERSION
fi
cd $GALAXY_VERSION
LOG_FILE=${GALAXY_VERSION}.log
if [ -f $LOG_FILE ] ; then
    /bin/rm -f $LOG_FILE
fi
# Setup and start Galaxy instance
setup_galaxy $GALAXY_VERSION 1>$LOG_FILE 2>&1
start_galaxy 1>$LOG_FILE 2>&1
#
# Set up API etc
GALAXY=nebulizer_test
MASTER_API_KEY=$(get_config_value master_api_key)
echo Master API key $MASTER_API_KEY
#
# Install and activate nebulizer
if [ ! -d venv.nebulizer ] ; then
    virtualenv venv.nebulizer
fi
. venv.nebulizer/bin/activate
if [ ! -z "$(pip list | grep nebulizer)" ] ; then
    echo -n Uninstalling existing nebulizer package...
    pip uninstall -y nebulizer 1>$LOG_FILE 2>&1
    echo done
fi
echo -n Installing nebulizer...
pip install $NEBULIZER_PKG 1>$LOG_FILE 2>&1
echo done
if [ ! -z "$BIOBLEND_VERSION" ] ; then
    echo -n Updating bioblend to version ${BIOBLEND_VERSION}...
    pip uninstall -y bioblend 1>$LOG_FILE 2>&1
    pip install bioblend==$BIOBLEND_VERSION 1>$LOG_FILE 2>&1
    echo done
fi
#
# Report installed package versions
echo "-------------------"
echo "Installed packages:"
echo "-------------------"
pip list
echo "-------------------"
#
# Add API key
if [ ! -e ~/.nebulizer ] || [ -z "$(grep ^$GALAXY ~/.nebulizer)" ] ; then
    echo -n Adding new API key for ${GALAXY}...
    nebulizer add_key $GALAXY http://127.0.0.1:8080 $MASTER_API_KEY 1>$LOG_FILE 2>&1
    echo done
else
    echo -n Updating API key for ${GALAXY}...
    nebulizer update_key --new-api-key $MASTER_API_KEY $GALAXY 1>$LOG_FILE 2>&1
    echo done
fi
#
# Get the test functions
test_cases="$(grep ^function ../test.cases.sh | cut -d' ' -f2 | cut -d'(' -f1)"
# Run tests
init_testing
for t in $test_cases ; do
    run_test $t
done
#
# Stop Galaxy
stop_galaxy 1>$LOG_FILE 2>&1
#
# Report the test results
finish_testing
exit $?
##
#
