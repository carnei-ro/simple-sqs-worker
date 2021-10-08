#!/bin/sh
#
# docker-entrypoint.sh
#
##

# shellcheck disable=SC2039

set -e
set -o pipefail

# Setup

: ${SQS_QUEUE_NAME:="my-queue"}
: ${AWS_REGION:="us-east-1"}
: ${LOG_LEVEL:="INFO"}

if [ -d /vault/secrets ]; then
    for i in $(ls -1 /vault/secrets); do
        source /vault/secrets/$i
    done
fi

msg()
{
    echo "{\"entrypoint\": \"$*\"}"
}


case $1 in
    app:run)
        msg "[INFO] Running application"

        cd "$APP_DIR"

        exec gosu "$APP_USER" python \
            sqs_consumer.py \
            --log="$LOG_LEVEL"
    ;;
esac


exec "$@"
