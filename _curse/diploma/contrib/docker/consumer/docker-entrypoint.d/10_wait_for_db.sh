#!/bin/sh

set -e

wait_for_db() {
  /app/contrib/docker/wait-for-it.sh "${DATABASE_HOST}:${DATABASE_PORT}" -t 30 -- echo "Database is ready"
}

wait_for_db

exit 0
