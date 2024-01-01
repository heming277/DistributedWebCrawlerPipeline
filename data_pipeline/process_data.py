# process_data.py
import pika
import json
from elasticsearch import Elasticsearch
import hashlib

# Set up Elasticsearch connection
es = Elasticsearch(['http://elasticsearch:9200'])

# Define a function to generate a unique ID
def generate_unique_id(data):
    unique_string = f"{data['title']}_{data['date']}"
    return hashlib.md5(unique_string.encode('utf-8')).hexdigest()

# Define the callback function
def callback(ch, method, properties, body):
    data = json.loads(body)
    print("Received data:", data)

    if data.get("type") == "final_message":
        print("Processing complete. Exiting...")
        with open('/tmp/processing_complete', 'w') as f:
            f.write('True')
        # Stop consuming and close the connection
        ch.stop_consuming()
    else:
        document_id = generate_unique_id(data)
        try:
            result = es.index(index="news_index", id=document_id, body=data)
            print("Index result:", result)
        except Exception as e:
            print("Error indexing document:", e)
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

# Set up RabbitMQ connection
connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='scrapy_queue')

# Start consuming messages from the queue
channel.basic_consume(queue='scrapy_queue', on_message_callback=callback, auto_ack=False)
print('Waiting for messages. To exit press CTRL+C')

try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("Interrupted by user, closing...")
finally:
    # Ensure the connection is closed properly
    if connection.is_open:
        connection.close()
    print("Connection closed.")
