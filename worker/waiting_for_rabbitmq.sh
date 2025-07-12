#!/bin/sh
set -e

echo "Waiting for RabbitMQ at $RABBITMQ_HOST:$RABBITMQ_PORT.."

until nc -z "$RABBITMQ_HOST" "$RABBITMQ_PORT"; do
  sleep 1
done

echo "RabbitMQ is up.."
exec "$@"
