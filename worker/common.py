import time
from signal import SIGINT, SIGTERM, signal

import logging
from json import loads

from prometheus_client import Gauge
sqs_queue_message_count = Gauge('sqs_queue_message_count', 'Number of Messages in SQS queue', ['queue_name'])


def process_message(sqs_message: str) -> None:
    logging.debug(f"processing message: {sqs_message}")
    msg = loads(sqs_message)
    if (msg['counter'] % 7) == 0:
        raise Exception("Sorry, no multiples of 7 allowed. Value: " + str(msg['counter']))
    pass


class SignalHandler:
    def __init__(self):
        self.received_signal = False
        signal(SIGINT, self._signal_handler)
        signal(SIGTERM, self._signal_handler)

    def _signal_handler(self, signal, frame):
        print(f"handling signal {signal}, exiting gracefully")
        self.received_signal = True


def wait(seconds: int):
    def decorator(fun):
        last_run = time.monotonic()

        def new_fun(*args, **kwargs):
            nonlocal last_run
            now = time.monotonic()
            if time.monotonic() - last_run > seconds:
                last_run = now
                return fun(*args, **kwargs)

        return new_fun

    return decorator


@wait(seconds=15)
def send_queue_metrics(sqs_queue) -> None:
    print("sending queue metrics")
    sqs_queue_message_count.labels(queue_name=queue_name(sqs_queue)).set(queue_length(sqs_queue))


def queue_length(sqs_queue) -> int:
    sqs_queue.load()
    return int(sqs_queue.attributes["ApproximateNumberOfMessages"])


def queue_name(sqs_queue) -> str:
    sqs_queue.load()
    return sqs_queue.attributes["QueueArn"].split(":")[-1]
