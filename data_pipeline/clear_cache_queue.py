from elasticsearch import Elasticsearch
import pika

def purge_rabbitmq_queue():
    try:
        # Set up RabbitMQ connection
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        # Purge the queue
        channel.queue_purge(queue='scrapy_queue')
        print("Queue purged successfully.")

        # Close the connection
        connection.close()
    except Exception as e:
        print(f"An error occurred while purging the RabbitMQ queue: {e}")

def delete_all_documents(es, index_name):
    try:
        response = es.delete_by_query(index=index_name, body={"query": {"match_all": {}}})
        print("All documents deleted from index:", response)
    except Exception as e:
        print(f"An error occurred while deleting documents: {e}")

def delete_index(es, index_name):
    try:
        response = es.indices.delete(index=index_name, ignore=[400, 404])
        print("Index deleted:", response)
    except Exception as e:
        print(f"An error occurred while deleting the index: {e}")

def main():
    # Ask to confirm
    confirm = input("Are you sure you want to delete all data from RabbitMQ and Elasticsearch? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Operation canceled.")
        return

    # Purge RabbitMQ queue
    purge_rabbitmq_queue()

    # Connect to the Elasticsearch server
    es = Elasticsearch(['http://localhost:9200'])

    # our index name
    index_name = "news_index"

    # Delete all documents and index
    delete_all_documents(es, index_name)
    delete_index(es, index_name)  

if __name__ == "__main__":
    main()