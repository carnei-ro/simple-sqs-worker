from os import getenv

import boto3

from common import SignalHandler, process_message, send_queue_metrics
from prometheus_client import start_http_server


from prometheus_client import Counter
sqs_queue_processed_messages = Counter('sqs_queue_processed_messages', 'Number of Processed Messages', ['queue_name', 'status'])

if getenv("PROFILE", "local") == "local":
    sqs = boto3.resource('sqs',
                         endpoint_url='http://sqs:9324',
                         region_name='elasticmq',
                         aws_secret_access_key='x',
                         aws_access_key_id='x',
                         use_ssl=False)
    queue = sqs.get_queue_by_name(QueueName=getenv("SQS_QUEUE_NAME", "my-queue"))
else:
    sqs = boto3.resource("sqs", region_name=getenv("AWS_REGION", "us-east-1"))
    queue = sqs.get_queue_by_name(QueueName=getenv("SQS_QUEUE_NAME", "my-queue"))


if __name__ == "__main__":
    start_http_server(8081)
    signal_handler = SignalHandler()
    while not signal_handler.received_signal:
        send_queue_metrics(queue)
        messages = queue.receive_messages(MaxNumberOfMessages=10, WaitTimeSeconds=1,)
        for message in messages:
            try:
                process_message(message.body)
            except Exception as e:
                print(f"exception while processing message: {repr(e)}")
                sqs_queue_processed_messages.labels(
                    queue_name=getenv("SQS_QUEUE_NAME", "my-queue"),
                    status="FAIL").inc()
                continue

            sqs_queue_processed_messages.labels(
                queue_name=getenv("SQS_QUEUE_NAME", "my-queue"),
                status="OK").inc()
            message.delete()
