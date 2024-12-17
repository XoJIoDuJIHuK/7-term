#!/bin/sh

set -e

insert_languages() {
  python src/manage.py insert-languages || true
}

insert_languages

exit 0
