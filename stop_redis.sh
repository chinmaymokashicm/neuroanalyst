#!/bin/bash

REDIS_DIR=$HOME/.local/redis
if [ -f "$REDIS_DIR/redis.pid" ]; then
    kill "$(cat $REDIS_DIR/redis.pid)"
    echo "Redis stopped."
else
    echo "Redis is not running (pid file not found)."
fi