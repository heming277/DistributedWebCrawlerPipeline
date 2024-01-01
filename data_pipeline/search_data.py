#search_data
from elasticsearch import Elasticsearch

# Function to get user input for the news source
def get_user_choice():
    sources = {
        "1": "OpenAI",
        "2": "Meta AI",
        "3": "Microsoft AI",
        "4": "Google AI",
        "5": "AWS Machine Learning",
        "6": "Apple Machine Learning",
        "7": "Mistral AI",
        "8": "All"
    }

    print("Select the news source to search for:")
    for key, value in sources.items():
        print(f"{key}: {value}")

    choice = input("Enter the number of your choice: ")
    return sources.get(choice, "Invalid")

# Set up Elasticsearch connection
es = Elasticsearch(['http://localhost:9200'])

# Get the user's choice
while True:
    user_choice = get_user_choice()
    if user_choice != "Invalid":
        break
    else:
        print("Invalid choice. Please enter a number from the list.")

# Build the query based on the user's choice
if user_choice == "All":
    query = {"match_all": {}}
else:
    query = {"match": {"source.keyword": user_choice}}

# Search for news items based on the user's choice
response = es.search(index="news_index", body={"query": query}, size=10000)

# Print out the hits in a meaningful way
print(f"Search results for news from {user_choice}:")
for hit in response['hits']['hits']:
    source = hit['_source']
    print(f"Source: {source['source']}")
    print(f"Title: {source['title']}")
    print(f"Date: {source['date']}")
    print(f"Link: {source.get('link', 'No link available')}")
    print("-" * 80)
