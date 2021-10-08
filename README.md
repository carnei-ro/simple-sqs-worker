# SQS Worker

Inspired by: https://perandrestromhaug.com/posts/writing-an-sqs-consumer-in-python/

## Demo

Start the worker and the mock for SQS (using [elasticmq](https://github.com/softwaremill/elasticmq))

```bash
docker-compose up --build
```

In other terminal open python (with boto3 installed) and execute the code:

```python
from os import getenv
import boto3

sqs = boto3.resource('sqs', endpoint_url='http://localhost:9324', region_name='elasticmq', aws_secret_access_key='x', aws_access_key_id='x', use_ssl=False)
queue = sqs.get_queue_by_name(QueueName=getenv('SQS_QUEUE_NAME', 'my-queue'))
for number in range(100):
    queue.send_message(MessageBody='{"hello": "world", "counter": '+str(number)+'}')
```

You can check the elasticmq console at http://localhost:9325 and also the worker metrics at http://localhost:8081
