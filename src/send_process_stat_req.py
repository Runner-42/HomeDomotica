#!/usr/bin/env python
import sys
import pika
import json

if len(sys.argv) == 2:
    queue_name = sys.argv[1]
else:
    print("Usage send_process_stat_req.py <Queue Name>")

message = {"Type": "Processing",
           "Event": "PRINT_PROCESS_STATUS"}

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue=queue_name)

channel.basic_publish(exchange='HOMEDOMOTICA',
                      routing_key=queue_name,
                      body=json.dumps(message))

print(" [x] Sent", json.dumps(message), " to ", queue_name)
connection.close()
