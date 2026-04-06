#!/bin/sh

echo "Running migrations..."
alembic downgrade base
alembic upgrade head

echo "Starting container CMD..."
exec "$@"
