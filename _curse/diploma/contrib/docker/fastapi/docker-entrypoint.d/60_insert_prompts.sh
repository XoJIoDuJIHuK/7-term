#!/bin/sh

set -e

insert_prompts() {
  python src/manage.py insert-prompts || true
}

insert_prompts

exit 0
