#!/usr/bin/env bash

APP_DIR="/usr/share/sonic/yang-utils"
APP_MODULE="main:app"

DEFAULT_SERVER_PORT=5000
SERVER_PORT=$DEFAULT_SERVER_PORT

echo "Starting Yang-Utils Gunicorn server on port $SERVER_PORT"

exec /usr/bin/gunicorn --workers 2 \
                      --bind 0.0.0.0:${SERVER_PORT} \
                      --chdir ${APP_DIR} \
                      ${APP_MODULE}