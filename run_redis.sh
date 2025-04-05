#!/bin/bash

screen -S redis
REDIS_DIR=$HOME/.local/redis
"$REDIS_DIR/bin/redis-server" "$REDIS_DIR/conf/redis.conf"
