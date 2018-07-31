import boto3
import logging
import json


class SQSHandler:

    # Get the service resource
    sqs = boto3.resource('sqs')
    queue = None
    logger = logging.getLogger()

    def __init__(self, queue_name):
        self.logger.debug("Configure SQS queue")
        try:
            # Get the queue. This returns an SQS.Queue instance
            self.queue = self.sqs.get_queue_by_name(QueueName=queue_name)
        except Exception:
            self.queue = self.sqs.create_queue(QueueName=queue_name)

    def send_message(self, body):
        try:
            return self.queue.send_message(MessageBody=json.dumps(body))
        except Exception as e:
            self.logger.debug(e)
            raise e
