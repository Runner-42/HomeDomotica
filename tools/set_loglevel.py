#!/usr/bin/env python
import sys
import pika

queue_name='IQ_RPI_INPUTBUTTON'

if len(sys.argv) == 3:
    queue_name = sys.argv[1]
    log_level = sys.argv[2]
if len(sys.argv) == 2:
    log_level = sys.argv[1]

event = "P;SET_LOG_LEVEL;" + log_level
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue=queue_name)

channel.basic_publish(exchange='',
                      routing_key=queue_name,
                      body=event)

print(" [x] Sent", event, " to", queue_name)
connection.close()
