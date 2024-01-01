# backend/app.py
from flask import Flask, jsonify
from flask_cors import CORS
from elasticsearch import Elasticsearch
import os
import time


app = Flask(__name__)
CORS(app)
es = Elasticsearch(['http://elasticsearch:9200'])

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200


@app.route('/articles', methods=['GET'])
def get_articles():
    try:
        # Fetch articles from Elasticsearch
        response = es.search(index="news_index", body={"query": {"match_all": {}}}, size=10000)
        articles = []
        for doc in response['hits']['hits']:
            source = doc['_source']
            article = {
                'id': doc['_id'],  # Include the Elasticsearch document ID
                'source': source.get('source', 'No source available'),
                'source_url': source.get('source_url', 'No source URL available'),  # Include the source URL
                'title': source.get('title', 'No title available'),
                'date': source.get('date', 'No date available'),
                'link': source.get('link', 'No link available')
            }
            articles.append(article)
        return jsonify(articles)
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Wait for the /tmp/processing_complete file to exist before starting the server
    while not os.path.exists('/tmp/processing_complete'):
        print("Waiting for data processing to complete...")
        time.sleep(5)
    
    print("Data processing complete, starting API service...")
    app.run(host='0.0.0.0', debug=True)