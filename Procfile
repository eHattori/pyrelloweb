web: $NEWRELIC_RUN uwsgi --master --http :$PORT --workers=$UWSGI_WORKERS --add-header Connection:\ Keep-Alive --http-auto-chunked --http-keepalive --pythonpath=django/pyrellowebapp --wsgi=django.pyrelloweb.wsgi --enable-threads --single-interpreter
release: python django/manage.py migrate --no-input
