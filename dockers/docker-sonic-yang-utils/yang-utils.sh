#!/usr/bin/env bash

SERVER_PORT=5000
MGMT_VARS_FILE=/usr/share/sonic/templates/yang_utils_vars.j2

if [ ! -f "$MGMT_VARS_FILE" ]; then
    echo "Yang Utils vars template file not found at $MGMT_VARS_FILE"
else
    MGMT_VARS=$(sonic-cfggen -d -t $MGMT_VARS_FILE)
    MGMT_VARS=${MGMT_VARS//[\']/\"} 
    X509=$(echo $MGMT_VARS | jq -r '.x509')
fi

if [ -n "$X509" ]; then
    SERVER_CRT=$(echo $X509 | jq -r '.server_crt // empty')
    SERVER_KEY=$(echo $X509 | jq -r '.server_key // empty')
fi

if [ -z "$SERVER_CRT" ] || [ -z "$SERVER_KEY" ] || [ ! -f "$SERVER_CRT" ] || [ ! -f "$SERVER_KEY" ]; then
    echo "Generating temporary TLS server certificate..."
    
    if [ -x "/usr/sbin/generate_cert" ]; then
        (cd /tmp && /usr/sbin/generate_cert --host="localhost,127.0.0.1")
    else
        (cd /tmp && openssl req -x509 -newkey rsa:4096 -nodes \
                            -keyout key.pem -out cert.pem \
                            -days 365 -subj "/CN=localhost")
    fi
    SERVER_CRT=/tmp/cert.pem
    SERVER_KEY=/tmp/key.pem
fi

GUNICORN_ARGS="--workers 4 --bind 0.0.0.0:$SERVER_PORT --chdir /usr/sbin main:app"

if [ -f "$SERVER_CRT" ] && [ -f "$SERVER_KEY" ]; then
    echo "Starting Yang-Utils Gunicorn server on port $SERVER_PORT with HTTPS"
    GUNICORN_ARGS+=" --keyfile $SERVER_KEY --certfile $SERVER_CRT"
else
    echo "Starting Yang-Utils Gunicorn server on port $SERVER_PORT without HTTPS (certs not found)."
fi

echo "Executing: gunicorn $GUNICORN_ARGS"
exec gunicorn $GUNICORN_ARGS
