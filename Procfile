web: gunicorn pyrelloweb.wsgi
release: python manage.py migrate --no-input --settings=pyrelloweb.settings
worker: celery --app=pyrelloweb worker --loglevel=INFO
