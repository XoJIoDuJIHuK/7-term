#!/bin/sh

set -e

upgrade_head() {
  alembic upgrade head || true
}
sleep 3
upgrade_head

exit 0
