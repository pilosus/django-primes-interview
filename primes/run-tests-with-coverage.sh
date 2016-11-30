#!/usr/bin/env bash

######################################################################
#       Run tests with coverage                                      #
######################################################################
#                                                                    #
# Usage:                                                             #
#  $ ./run-tests-with-coverage.sh [myapp]                            #
#      myapp: an application to run tests against.                   #
#                                                                    #
# Requirements:                                                      #
#  $ pip install -r requirements/tesging.txt                         #
#                                                                    #
######################################################################

if [ -z "$1" ] ; then
    myapp="datasets"
else
    myapp="$1"
fi

coverage run --source='.' manage.py test $myapp
coverage html
coverage report

separator="--------------------------------------------------------------------"

echo $separator
echo "IMPORTANT! HTML report created under htmlcov directory"
echo $separator

exit 0
