#!/usr/bin/env bash
set -e

# Get the listen port for uWSGI, default to 80
USE_SOCKET=${SOCKET:-8080}


if [ -f ./uwsgi.ini ]; then
    cp ./uwsgi.ini /app/uwsgi.ini
else
    content='[uwsgi]\n'
    content=$content'chdir                   = /app\n'
    content=$content"socket                  = :${USE_SOCKET}\n"
    content=$content'wsgi-file               = run.py\n'
    content=$content'callable                = run\n'
    content=$content'master                  = true\n'
    content=$content'stdout_logfile          = /dev/stdout\n'
    content=$content'stdout_logfile_maxbytes = 0\n'
    content=$content'stderr_logfile          = /dev/stderr\n'
    content=$content'stderr_logfile_maxbytes = 0\n'

    # Save generated ini file
    printf "$content" > /app/uwsgi.ini
fi

exec "$@"
