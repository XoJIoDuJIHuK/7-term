#!/bin/sh

set -e

create_admin() {
  python src/manage.py create-admin || true
}

create_admin

exit 0
