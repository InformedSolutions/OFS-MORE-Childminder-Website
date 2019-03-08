import boto3
import logging
import json

from django.conf import settings

logger = logging.getLogger()


class SQSHandler:
    """
    Class for managing interactions with an Amazon SQS endpoint
    """

    # Get the service resource
    session = None
    sqs = None
    queue = None
    logger = logging.getLogger()

    def __init__(self, queue_name):
        """
        Default constructor
        :param queue_name: The name of the queue to publish messages to.
        """
        self.logger.debug("Configuring SQS queue")

        try:
            self.session = boto3.Session(
                aws_access_key_id=settings.AWS_SQS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SQS_SECRET_ACCESS_KEY,
                region_name='eu-west-2'
            )

            # Get the queue. This returns an SQS.Queue instance
            self.sqs = self.session.resource('sqs')
            self.queue = self.sqs.get_queue_by_name(QueueName=queue_name)
        except Exception as e:
            logger.error(e)
            self.queue = self.sqs.create_queue(QueueName=queue_name)

    def send_message(self, body):
        """
        Genericised method for publishing a message to an SQS queue
        """
        try:
            response = self.queue.send_message(MessageBody=json.dumps(body))
            return response
        except Exception as e:
            self.logger.debug(e)
            raise e
