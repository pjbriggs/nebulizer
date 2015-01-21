#!/bin/sh -e
#
# Create a batch of user accounts in a Galaxy instance
#
function usage() {
    echo "$(basename $0) GALAXY_URL API_KEY TEMPLATE START END PASSWORD"
    echo 
    echo "Create multiple user accounts in GALAXY_URL based on TEMPLATE"
    echo "email address."
    echo 
    echo "TEMPLATE should include # symbol indicating where an integer"
    echo "index should be substituted (e.g. 'student#@galaxy.ac.uk')."
    echo "START and END are the range of ids to create (e.g. 1 to 10)."
    echo 
    echo "All accounts will be created with the same PASSWORD."
    echo 
    echo "For example:"
    echo 
    echo "$(basename $0) <URL> <KEY> student#@galaxy.ac.uk 1 5 <PASSWD>"
    echo 
    echo "will create 5 accounts called student1@galaxy.ac.uk to"
    echo "student5@galaxy.ac.uk."
}
function make_email() {
    echo $(echo $1 | cut -d'#' -f1)${2}$(echo $1 | cut -d'#' -f2)
}
# Check command line
if [ $# -ne 6 ] ; then
    usage
    exit 1
fi
GALAXY_URL=$1
API_KEY=$2
TEMPLATE=$3
START=$4
END=$5
PASSWD=$6
# Create batch of users
echo "*** Checking that all accounts can be created ***"
for i in $(seq $START $END) ; do
    email=$(make_email $TEMPLATE $i)
    ./create_user.py -c $GALAXY_URL $API_KEY $email
done
echo "Ok"
echo "*** Creating accounts ***"
for i in $(seq $START $END) ; do
    email=$(make_email $TEMPLATE $i)
    ./create_user.py -p $PASSWD $GALAXY_URL $API_KEY $email
done
##
#

