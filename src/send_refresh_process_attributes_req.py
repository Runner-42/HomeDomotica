#!/usr/bin/env python
import sys
import pika

if len(sys.argv) == 2:
    queue_name = sys.argv[1]
else:
    print("Usage send_refresh_process_attributes_req.py <Queue Name>")

event = "P;REFRESH_PROCESS_ATTRIBUTES"

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue=queue_name)

channel.basic_publish(exchange='HOMEDOMOTICA',
                      routing_key=queue_name,
                      body=event)

print(" [x] Sent", event, " to", queue_name)
connection.close()
