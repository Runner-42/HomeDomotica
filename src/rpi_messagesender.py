'''
Name:		RPiMessageSender.py
Purpose:	Class RPiMessageSender is used to send messages to a queue

Author:	Wim

Created:	20/08/2018
Copyright:	(c) Wim 2018
Licence:
'''
import pika

class RPiMessageSender():
    '''
    This class is created to allow sending messages to a specific queue
    Following attributes are defined:
        - queue_name => Name of the message queue
        - connection => Handle to the connection to the message queue
        - channel => Handle to the channel within the connection
    Queue's are created by the "receiver". In case a queue doesn't exist
    an error message is logged and no instance of the RPiMessageSender class
    is created
    '''
    def __init__(self, config=None, log_handler=None):
        # Initiate Logger function so we can start logging stuf
        self.logger_instance = log_handler

        self.config = config
        self.config['host'] = config.get('host', 'localhost')
        self.config['exchangeName'] = config.get('exchangeName', 'HOMEDOMOTICA')
        self.config['port'] = config.get('port', 5672)
        self.config['virtualHost'] = config.get('virtualHost', '/')

    def __repr__(self):
        return self.config

    def _create_connection(self):
        parameters = pika.ConnectionParameters(self.config['host'],
                                               self.config['port'],
                                               self.config['virtualHost'])

        return pika.BlockingConnection(parameters)

    def send_message(self, queue_list, message):
        '''
        method that will
        1) connect to a message exchange
        2) send a message to this message exchange
        3) disconnects from the message exchage
        '''
        connection = None
        try:
            connection = self._create_connection()
            channel = connection.channel()

            channel.exchange_declare(exchange=self.config['exchangeName'],
                                     passive=True)

            if queue_list is not None:
                for routingkey in queue_list:
                    channel.basic_publish(exchange=self.config['exchangeName'],
                                          routing_key=routingkey,
                                          body=message)
                    if self.logger_instance is not None:
                        self.logger_instance.debug(
                            "RPiMessageSender - send message {} to queue {}".format(
                                message,
                                routingkey)
                            )
        except Exception as err:    # pylint: disable=broad-except
            if self.logger_instance is not None:
                self.logger_instance.error(
                    "RPiMessageSender - Unable to send message {} to queue(s) {} - {}".format(
                        message,
                        queue_list,
                        err))
        finally:
            if connection:
                connection.close()

def main():
    '''
    main function used mainly for testing purposes
    '''
    print("Hello world! I'm the Message Sender class")
    message_sender_instance = RPiMessageSender()
    queue_list = ["TESTQUEUE"]
    message_sender_instance.send_message(queue_list, "Test message")
    print("Bye world")

if __name__ == '__main__':
    main()
