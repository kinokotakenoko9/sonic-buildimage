#!/usr/bin/env bash

SERVER_PORT=5000

echo "Starting Yang-Utils Gunicorn server on port $SERVER_PORT"

exec python /usr/sbin/main.py