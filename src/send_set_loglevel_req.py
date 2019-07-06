#!/usr/bin/env python
import sys
import pika

if len(sys.argv) == 2:
    queue_name = sys.argv[1]
    log_level = "INFO"
elif len(sys.argv) == 3:
    queue_name = sys.argv[1]
    log_level = sys.argv[2]
else:
    print("Usage send_set_loglevel_req.py <Queue Name> <Log level (Default=INFO)>")


event = "P;SET_LOG_LEVEL;" + log_level

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue=queue_name)

channel.basic_publish(exchange='HOMEDOMOTICA',
                      routing_key=queue_name,
                      body=event)

print(" [x] Sent", event, " to", queue_name)
connection.close()
