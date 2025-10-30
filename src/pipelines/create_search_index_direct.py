import os
import json
import requests
from dotenv import load_dotenv
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential

load_dotenv()

# Configuration
SEARCH_ENDPOINT = os.environ.get("SEARCH_ENDPOINT")
SEARCH_KEY = os.environ.get("SEARCH_KEY") 
INDEX_NAME = os.environ.get("INDEX_NAME")
COSMOS_ENDPOINT = os.environ.get("COSMOS_ENDPOINT")

print(f"Search Endpoint: {SEARCH_ENDPOINT}")
print(f"Index Name: {INDEX_NAME}")

# Headers for Azure Search REST API
headers = {
    'Content-Type': 'application/json',
    'api-key': SEARCH_KEY
}

# Create Index Schema (without data source dependency)
index_definition = {
    "name": INDEX_NAME,
    "fields": [
        {
            "name": "id",
            "type": "Edm.String",
            "key": True,
            "searchable": False,
            "filterable": True,
            "retrievable": True
        },
        {
            "name": "ProductID",
            "type": "Edm.String",
            "searchable": False,
            "filterable": True,
            "retrievable": True
        },
        {
            "name": "ProductName",
            "type": "Edm.String",
            "searchable": True,
            "filterable": False,
            "retrievable": True,
            "analyzer": "standard.lucene"
        },
        {
            "name": "ProductCategory",
            "type": "Edm.String",
            "searchable": True,
            "filterable": True,
            "facetable": True,
            "retrievable": True
        },
        {
            "name": "ProductDescription",
            "type": "Edm.String", 
            "searchable": True,
            "filterable": False,
            "retrievable": True,
            "analyzer": "standard.lucene"
        },
        {
            "name": "ProductPrice",
            "type": "Edm.Double",
            "searchable": False,
            "filterable": True,
            "sortable": True,
            "facetable": True,
            "retrievable": True
        },
        {
            "name": "ProductImageURL",
            "type": "Edm.String",
            "searchable": False,
            "filterable": False,
            "retrievable": True
        },
        {
            "name": "content_for_vector",
            "type": "Edm.String",
            "searchable": True,
            "filterable": False,
            "retrievable": True,
            "analyzer": "standard.lucene"
        }
    ]
}

def create_index():
    """Create the search index"""
    url = f"{SEARCH_ENDPOINT}/indexes/{INDEX_NAME}?api-version=2023-11-01"
    
    response = requests.put(url, json=index_definition, headers=headers)
    
    if response.status_code in [200, 201, 204]:
        print(f"✅ Search index '{INDEX_NAME}' created successfully")
        return True
    else:
        print(f"❌ Failed to create index: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def get_cosmos_data():
    """Get data from Cosmos DB using Azure AD auth"""
    try:
        credential = DefaultAzureCredential()
        client = CosmosClient(COSMOS_ENDPOINT, credential)
        database = client.get_database_client("zava")
        container = database.get_container_client("product_catalog")
        
        # Get all items from container
        items = list(container.read_all_items())
        print(f"Retrieved {len(items)} items from Cosmos DB")
        return items
    except Exception as e:
        print(f"Error retrieving data from Cosmos DB: {e}")
        return []

def upload_to_search_index(documents):
    """Upload documents directly to the search index"""
    if not documents:
        print("No documents to upload")
        return False
    
    # Prepare documents for search index
    search_documents = []
    for doc in documents:
        search_doc = {
            "id": str(doc.get("id", doc.get("ProductID", ""))),
            "ProductID": str(doc.get("ProductID", "")),
            "ProductName": doc.get("ProductName", ""),
            "ProductCategory": doc.get("ProductCategory", ""), 
            "ProductDescription": doc.get("ProductDescription", ""),
            "ProductPrice": float(doc.get("ProductPrice", 0)) if doc.get("ProductPrice") else 0.0,
            "ProductImageURL": doc.get("ProductImageURL", ""),
            "content_for_vector": doc.get("content_for_vector", "")
        }
        search_documents.append(search_doc)
    
    # Upload in batches
    batch_size = 50
    total_uploaded = 0
    
    for i in range(0, len(search_documents), batch_size):
        batch = search_documents[i:i + batch_size]
        
        # Create upload batch
        upload_batch = {
            "value": [{"@search.action": "mergeOrUpload", **doc} for doc in batch]
        }
        
        url = f"{SEARCH_ENDPOINT}/indexes/{INDEX_NAME}/docs/index?api-version=2023-11-01"
        response = requests.post(url, json=upload_batch, headers=headers)
        
        if response.status_code in [200, 207]:
            total_uploaded += len(batch)
            print(f"✅ Uploaded batch {i//batch_size + 1}: {len(batch)} documents")
        else:
            print(f"❌ Failed to upload batch {i//batch_size + 1}: {response.status_code}")
            print(f"Response: {response.text}")
    
    print(f"🎉 Total documents uploaded: {total_uploaded}")
    return total_uploaded > 0

def main():
    print("🚀 Creating Azure AI Search index and uploading data...")
    
    # Step 1: Create index
    print("\n🔍 Step 1: Creating search index...")
    if not create_index():
        return
    
    # Step 2: Get data from Cosmos DB
    print("\n📊 Step 2: Retrieving data from Cosmos DB...")
    documents = get_cosmos_data()
    
    if not documents:
        print("❌ No data retrieved from Cosmos DB")
        return
    
    # Step 3: Upload data to search index
    print(f"\n📤 Step 3: Uploading {len(documents)} documents to search index...")
    if upload_to_search_index(documents):
        print("\n🎉 Successfully created search index and uploaded data!")
        print(f"📍 Your search index '{INDEX_NAME}' is ready to use.")
    else:
        print("\n❌ Failed to upload data to search index")

if __name__ == "__main__":
    main()