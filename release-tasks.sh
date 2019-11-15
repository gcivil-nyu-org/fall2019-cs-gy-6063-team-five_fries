#!/bin/sh
python manage.py migrate --noinput

# run this only on the integration heroku instance
if [[ ! -z "$DEVELOP"  ]]; then
  python manage.py loaddata locations.json
fi
