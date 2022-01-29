#!/bin/sh
wdir="$PWD"; [ "$PWD" = "/" ] && wdir=""
case "$0" in
  /*) scriptdir="${0}";;
  *) scriptdir="$wdir/${0#./}";;
esac
scriptdir="${scriptdir%/*}"

# Djano jobs
python $scriptdir/../unicorn/manage.py cleartokens
python $scriptdir/../unicorn/manage.py clearsessions
