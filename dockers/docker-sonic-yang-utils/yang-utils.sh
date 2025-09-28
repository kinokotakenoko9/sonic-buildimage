#!/usr/bin/env bash

# Startup script for SONiC yang utils server
EXIT_YANG_UTILS_VARS_FILE_NOT_FOUND=1
YANG_UTILS_VARS_FILE=/usr/share/sonic/templates/yang_utils.j2

if [ ! -f "$YANG_UTILS_VARS_FILE" ]; then
    echo "Yang utils vars template file not found"
    exit $EXIT_YANG_UTILS_VARS_FILE_NOT_FOUND
fi

# Read basic server settings from yang utils vars entries
YANG_UTILS_VARS=$(sonic-cfggen -d -t $YANG_UTILS_VARS_FILE)
YANG_UTILS_VARS=${YANG_UTILS_VARS//[\']/\"}

YANG_UTILS=$(echo $MGMT_VARS | jq -r '.yang_utils')

if [ -n "$YANG_UTILS" ]; then
    SERVER_PORT=$(echo $YANG_UTILS | jq -r '.port')
    LOG_LEVEL=$(echo $YANG_UTILS | jq -r '.log_level')
else
    SERVER_PORT=5000
    LOG_LEVEL=5
fi

YANG_UTILS_ARGS="-logtostderr"
[ ! -z $SERVER_PORT ] && YANG_UTILS_ARGS+=" -port $SERVER_PORT"
[ ! -z $LOG_LEVEL   ] && YANG_UTILS_ARGS+=" -v $LOG_LEVEL"

echo "YANG_UTILS_ARGS = $YANG_UTILS_ARGS"

export CVL_SCHEMA_PATH=/usr/sbin/schema

exec /usr/sbin/yang_utils ${YANG_UTILS_ARGS}