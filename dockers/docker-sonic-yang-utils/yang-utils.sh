#!/usr/bin/env bash

DEFAULT_SERVER_PORT=5000
SERVER_PORT=$DEFAULT_SERVER_PORT

YANG_UTILS_VARS_FILE=/usr/share/sonic/templates/yang_utils_vars.j2
if [ -f "$YANG_UTILS_VARS_FILE" ]; then
    CONFIGURED_PORT=$(sonic-cfggen -d -t $YANG_UTILS_VARS_FILE | jq -r '.yang_utils.port // empty')
    if [ -n "$CONFIGURED_PORT" ]; then
        SERVER_PORT=$CONFIGURED_PORT
    fi
fi

echo "Starting yang-utils Gunicorn server on port $SERVER_PORT"

APP_DIR="/usr/share/sonic/yang-utils/"

exec /usr/bin/gunicorn --workers 3 \
                      --bind 0.0.0.0:${SERVER_PORT} \
                      --chdir ${APP_DIR} \
                      -m 007 \
                      wsgi:app