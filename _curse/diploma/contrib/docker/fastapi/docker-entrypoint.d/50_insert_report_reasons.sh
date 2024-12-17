#!/bin/sh

set -e

insert_report_reasons() {
  python src/manage.py insert-report-reasons || true
}

insert_report_reasons

exit 0
