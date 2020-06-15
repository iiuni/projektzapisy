#!/bin/bash

NAME="zapisy"                                                  # Name of the application
DJANGODIR=/home/*user*/deploy/current/zapisy                   # Django project directory
SOCKFILE=/home/*user*/deploy/current/env3/run/gunicorn.sock    # we will communicte using this unix socket
USER=*user*                                                    # the user to run as
GROUP=*user*                                                   # the group to run as
CPU=$(nproc)
NUM_WORKERS=$((($CPU*2)+1))                         # how many worker processes should Gunicorn spawn
                                                    # Gunicorn documentation recommend (2*CPU)+1 as the number of workers to start off with
DJANGO_SETTINGS_MODULE=zapisy.settings              # which settings file should Django use
DJANGO_WSGI_MODULE=zapisy.wsgi                      # WSGI module name
echo "Starting $NAME as `whoami`"

# Create link to socket for Nginx
ln -sf /home/*user*/deploy/current/env3/run /home/*user*/deploy/current/zapisy/socket

# Activate the virtual environment

cd $DJANGODIR
source /home/*user*/deploy/current/env3/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist

RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)

exec /home/*user*/deploy/current/env3/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --bind=unix:$SOCKFILE \
  --log-level=debug \
  --log-file=-
