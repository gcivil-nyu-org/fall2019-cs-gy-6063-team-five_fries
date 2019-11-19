worker: celery -A citystreets.celery worker -l DEBUG -E
release: ./release-tasks.sh
web: gunicorn citystreets.wsgi --log-file -
