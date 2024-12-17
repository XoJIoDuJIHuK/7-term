#!/bin/sh

set -e

insert_models() {
  python src/manage.py insert-models || true
}

insert_models

exit 0
