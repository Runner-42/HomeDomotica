'''
Name:		RPiMessageConsumer.py
Purpose:	Class RPiMessageConsumer is used to create a queue on RabbitMQ and read messages
            from this queue

Author:	Wim

Created:	22/08/2018
Copyright:	(c) Wim 2018
Licence:
'''
import time
import pika

class RPiMessageConsumer():
    '''
    This class is created to handle the Message queue for a specific queue
    It's been implemented as a Context Manager, so it should be invoke sing the 'with' statement
    The constructure takes 1 parameter which is a dictionary holding following (mandatory)
    key entries, with their respective values. Except for the 'queueName' and 'routingKey'
    default values are included when ommited
    - 'queueName'
    - 'exchangeName'
    - 'routingKey'
    - 'host'
    - 'exchangeType'
    - 'exchangePassive'
    - 'exchangeDurable'
    - 'exchangeAutoDelete'
    - 'exchangeInternal'
    - 'queuePassive'
    - 'queueDurable'
    - 'queueExclusive'
    - 'queueAutoDelete'
    - 'sleepTime'
    After creation of the RPiMessageConsumer instance, reading messages from the queue can be
    invoked using the "consume" method. This method takes 2 call back functions as paramaters
    - the first function is triggered when a message was read from the queue
        => the message that was received is passed as parameter to this call back function
           so it can be used in the calling function
        => this function must return a boolean:
            - True => Loop to check messages on the queue is continuing
            - False => Loop to check queue is stopped
    - the second function is run when no message was available on the queue
    - A sleep time, provided by the 'sleepTime' configuration parameter each time no message was
      found on the queue
    '''

    def __init__(self, config):
        if config.get('queueName') is None:
            self.config = None
        else:
            self.config = {}
            self.config['queueName'] = config.get('queueName')
            self.config['routingKey'] = config.get('routingKey', self.config['queueName'])
            self.config['exchangeName'] = config.get('exchangeName', 'HOMEDOMOTICA')
            self.config['host'] = config.get('host', 'localhost')
            self.config['exchangeType'] = config.get('exchangeType', 'direct')
            self.config['exchangePassive'] = config.get('exchangePassive', False)
            self.config['exchangeDurable'] = config.get('exchangeDurable', True)
            self.config['exchangeAutoDelete'] = config.get('exchangeAutoDelete', False)
            self.config['exchangeInternal'] = config.get('exchangeInternal', True)
            self.config['queuePassive'] = config.get('queuePassive', False)
            self.config['queueDurable'] = config.get('queueDurable', False)
            self.config['queueExclusive'] = config.get('queueExclusive', False)
            self.config['queueAutoDelete'] = config.get('queueAutoDelete', False)
            self.config['sleepTime'] = config.get('sleepTime', 0.1)

    def __enter__(self):
        self.connection = self._create_connection() # pylint: disable=attribute-defined-outside-init
        return self

    def __exit__(self, *args):
        self.connection.close()

    def consume(self, message_received_callback, no_message_received_callback):
        '''
        This method is used to create and monitor the queue. In case a message is received
        the 'message-received_callback' function is executed.
        In case no message was gound on the queue, the 'no_massge_received_callback'
        function is triggered.
        Implementation of both functions should be done in the "calling" process
        The "message_received_callback" will be passed the message recived as a paramater
        This function should return a True or False status to indicate if the queue monitoring
        should be stopped or not.
        '''
        channel = self.connection.channel()

        self._create_exchange(channel)
        self._create_queue(channel)

        channel.queue_bind(queue=self.config['queueName'],
                           exchange=self.config['exchangeName'],
                           routing_key=self.config['routingKey'])

        run_message_pump = True
        while run_message_pump is True:
            method, header, body = channel.basic_get(queue=self.config['queueName'])    # pylint: disable=unused-variable
            if method is None:
                no_message_received_callback()
                time.sleep(self.config['sleepTime'])
            else:
                run_message_pump = message_received_callback(body.decode())
                channel.basic_ack(delivery_tag=method.delivery_tag)

    def _create_exchange(self, channel):
        channel.exchange_declare(exchange=self.config['exchangeName'],
                                 exchange_type=self.config['exchangeType'],
                                 passive=self.config['exchangePassive'],
                                 durable=self.config['exchangeDurable'],
                                 auto_delete=self.config['exchangeAutoDelete'],
                                 internal=self.config['exchangeInternal'])

    def _create_queue(self, channel):
        channel.queue_declare(queue=self.config['queueName'],
                              passive=self.config['queuePassive'],
                              durable=self.config['queueDurable'],
                              exclusive=self.config['queueExclusive'],
                              auto_delete=self.config['queueAutoDelete'])

    def _create_connection(self):
        parameters = pika.ConnectionParameters(self.config['host'])

        return pika.BlockingConnection(parameters)

    def __repr__(self):
        return self.config

def main():
    '''
    main function used mainly for testing purposes
    '''
    def my_function(message):
        print("message= ", message)
        if message[:4] == "STOP":
            return False
        return True

    def my_other_function():
        print("Not doing much")

    message_configuration = {'queueName': "TESTQUEUE",
                             'host': 'localhost',
                             'exchangeName': "HomeDomotica",
                             'routingKey': "TESTQUEUE"}

    print("Hello world! I'm the Message Consumer class")
    with RPiMessageConsumer(message_configuration) as consumer:
        consumer.consume(my_function, my_other_function)

    print("Bye world")

if __name__ == '__main__':
    main()
