#!/usr/bin/env bash
set -euo pipefail

# Initialize with empty value bye default
DATABASE_URL=${DATABASE_URL:-""}

# Do not run if `manage.py` is not present.
if [[ $@ == *"manage.py runserver"*  && ! -f "manage.py" ]]
then
    >&2 echo "manage.py not found. Make sure mounts are syncing."
    exit
fi

# Wait for Postgres for Django related commands.
if [[ $@ == *"manage.py "* && ! -z ${DATABASE_HOST+x} && -z ${DATABASE_URL+x} ]]
then
    RETRIES=60
    >&2 echo "Waiting for Postgres"
    until PGPASSWORD=$DATABASE_PASSWORD pg_isready -h $DATABASE_HOST -p $DATABASE_PORT -U $DATABASE_USER ; do
        if [ $RETRIES -eq 0 ]; then
            >&2 echo "Exiting"
            exit
        fi
        >&2 echo "Waiting for Postgres server, $((RETRIES--)) remaining attempts"
        sleep 1
    done
fi

# Run only if django server is being run.
if [[ $@ == *"manage.py runserver"* ]]
then
    # Translations
    >&2 echo "Compiling Django translations (background job)"
    python manage.py compilemessages &

    # Migrations
    >&2 echo "Running Django migrations (background job)"
    python manage.py migrate --noinput &
    python manage.py createcachetable &

    # PIP requirements for easy Heroku deploy
    >&2 echo "Freezing requirements (background job)"
    poetry export -f requirements.txt -o requirements.txt &
fi

# Run only if django-q cluster is being run.
#if [[ $@ == *"manage.py qcluster"* ]]
#then
##    # Tasks
##    >&2 echo "Create task schedules"
##    python manage.py runscript schedule_tasks
#fi

exec "$@"
