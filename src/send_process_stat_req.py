#!/usr/bin/env python
import sys
import pika

if len(sys.argv) == 2:
    queue_name = sys.argv[1]
else:
    print("Usage send_process_stat_req.py <Queue Name>")

event = "P;PRINT_PROCESS_STATUS"

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue=queue_name)

channel.basic_publish(exchange='HOMEDOMOTICA',
                      routing_key=queue_name,
                      body=event)

print(" [x] Sent", event, " to ",queue_name)
connection.close()
