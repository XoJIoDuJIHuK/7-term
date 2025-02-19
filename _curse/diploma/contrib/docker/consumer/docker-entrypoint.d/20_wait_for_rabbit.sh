#!/bin/sh

set -e

wait_for_rabbit() {
  /app/contrib/docker/wait-for-it.sh "${RABBIT_HOST}" -t 30 -- echo "Rabbit is ready"
}

wait_for_rabbit

exit 0
