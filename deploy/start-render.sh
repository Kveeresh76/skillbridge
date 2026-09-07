#!/bin/sh
set -eu

if [ "${ENVIRONMENT:-production}" = "production" ]; then
	if [ -z "${DATABASE_URL:-}" ]; then
		echo "DATABASE_URL is required in production. Set it to the Render PostgreSQL internal connection string."
		exit 1
	fi
	case "$DATABASE_URL" in
		*localhost*|*127.0.0.1*)
			echo "DATABASE_URL points to localhost. Set it to the Render PostgreSQL internal connection string."
			exit 1
			;;
	esac
fi

alembic upgrade head
exec supervisord -c /etc/supervisor/conf.d/supervisord.conf
