web: gunicorn biblored.wsgi --config gunicorn_config.py
worker: python manage.py qcluster
release: python manage.py migrate
