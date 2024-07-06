#!/usr/bin/env bash

python3.11 manage.py migrate --noinput
/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
exec "$@"
