#!/bin/sh

set -e

wait_for_kafka() {
  /app/contrib/docker/wait-for-it.sh "${KAFKA_ADDRESS}" -t 30 -- echo "Kafka is ready"
}

wait_for_kafka

exit 0
