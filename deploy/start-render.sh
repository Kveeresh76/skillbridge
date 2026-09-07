#!/bin/sh
set -eu

alembic upgrade head
exec supervisord -c /etc/supervisor/conf.d/supervisord.conf
