#!/bin/sh
set -e

echo "CHeck RabbitMQ.."
./waiting_for_rabbitmq.sh

echo "Starting Python worker.."
exec python -m app.main
