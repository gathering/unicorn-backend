#!/bin/sh
wdir="$PWD"; [ "$PWD" = "/" ] && wdir=""
case "$0" in
  /*) scriptdir="${0}";;
  *) scriptdir="$wdir/${0#./}";;
esac
scriptdir="${scriptdir%/*}"

# Competition jobs
python $scriptdir/../unicorn/manage.py update_competition_states
python $scriptdir/../unicorn/manage.py entry_status_progress
