import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# Configuration from .env file
SEARCH_ENDPOINT = os.environ.get("SEARCH_ENDPOINT")
SEARCH_KEY = os.environ.get("SEARCH_KEY")
INDEX_NAME = os.environ.get("INDEX_NAME")
COSMOS_ENDPOINT = os.environ.get("COSMOS_ENDPOINT")
COSMOS_KEY = os.environ.get("COSMOS_KEY")
DATABASE_NAME = os.environ.get("DATABASE_NAME")
CONTAINER_NAME = os.environ.get("CONTAINER_NAME")

print(f"Search Endpoint: {SEARCH_ENDPOINT}")
print(f"Index Name: {INDEX_NAME}")

# Headers for Azure Search REST API
headers = {
    'Content-Type': 'application/json',
    'api-key': SEARCH_KEY
}

# Step 1: Create Data Source (using Managed Identity)
datasource_definition = {
    "name": "cosmosdb-datasource",
    "description": "Cosmos DB data source for product catalog",
    "type": "cosmosdb",
    "credentials": {
        "connectionString": f"ResourceId=/subscriptions/463a82d4-1896-4332-aeeb-618ee5a5aa93/resourceGroups/techworkshop-l300-ai-agents-centralus/providers/Microsoft.DocumentDB/databaseAccounts/owrgnenm7wj2y-cosmosdb;Database={DATABASE_NAME}"
    },
    "container": {
        "name": CONTAINER_NAME,
        "query": "SELECT * FROM c WHERE c._ts >= @HighWaterMark ORDER BY c._ts"
    },
    "dataChangeDetectionPolicy": {
        "@odata.type": "#Microsoft.Azure.Search.HighWaterMarkChangeDetectionPolicy",
        "highWaterMarkColumnName": "_ts"
    },
    "identity": {
        "@odata.type": "#Microsoft.Azure.Search.DataSystemAssignedIdentity"
    }
}

# Step 2: Create Index Schema
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

# Step 3: Create Indexer
indexer_definition = {
    "name": f"{INDEX_NAME}-indexer",
    "description": "Indexer for product catalog data from Cosmos DB",
    "dataSourceName": "cosmosdb-datasource",
    "targetIndexName": INDEX_NAME,
    "schedule": {
        "interval": "PT24H"  # Run once per day
    },
    "parameters": {
        "batchSize": 50,
        "maxFailedItems": 10,
        "maxFailedItemsPerBatch": 5
    }
}

def create_or_update_datasource():
    """Create or update the Cosmos DB data source"""
    url = f"{SEARCH_ENDPOINT}/datasources/{datasource_definition['name']}?api-version=2023-11-01"
    
    # Try to create new datasource
    response = requests.put(url, json=datasource_definition, headers=headers)
    
    if response.status_code in [200, 201]:
        print(f"✅ Data source '{datasource_definition['name']}' created/updated successfully")
        return True
    else:
        print(f"❌ Failed to create data source: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def create_or_update_index():
    """Create or update the search index"""
    url = f"{SEARCH_ENDPOINT}/indexes/{INDEX_NAME}?api-version=2023-11-01"
    
    response = requests.put(url, json=index_definition, headers=headers)
    
    if response.status_code in [200, 201]:
        print(f"✅ Search index '{INDEX_NAME}' created/updated successfully")
        return True
    else:
        print(f"❌ Failed to create index: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def create_or_update_indexer():
    """Create or update the indexer"""
    url = f"{SEARCH_ENDPOINT}/indexers/{indexer_definition['name']}?api-version=2023-11-01"
    
    response = requests.put(url, json=indexer_definition, headers=headers)
    
    if response.status_code in [200, 201]:
        print(f"✅ Indexer '{indexer_definition['name']}' created/updated successfully")
        return True
    else:
        print(f"❌ Failed to create indexer: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def run_indexer():
    """Run the indexer to import data"""
    url = f"{SEARCH_ENDPOINT}/indexers/{indexer_definition['name']}/run?api-version=2023-11-01"
    
    response = requests.post(url, headers=headers)
    
    if response.status_code == 202:
        print(f"✅ Indexer '{indexer_definition['name']}' started successfully")
        return True
    else:
        print(f"❌ Failed to run indexer: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def check_indexer_status():
    """Check the status of the indexer"""
    url = f"{SEARCH_ENDPOINT}/indexers/{indexer_definition['name']}/status?api-version=2023-11-01"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        status = response.json()
        print(f"Indexer Status: {status.get('status', 'Unknown')}")
        if 'lastResult' in status:
            last_result = status['lastResult']
            print(f"Last Run Status: {last_result.get('status', 'Unknown')}")
            print(f"Items Processed: {last_result.get('itemCount', 0)}")
            if 'errorMessage' in last_result:
                print(f"Error: {last_result['errorMessage']}")
        return True
    else:
        print(f"❌ Failed to get indexer status: {response.status_code}")
        return False

def main():
    print("🚀 Starting Azure AI Search index creation and data import process...")
    
    # Step 1: Create data source
    print("\n📊 Step 1: Creating Cosmos DB data source...")
    if not create_or_update_datasource():
        return
    
    # Step 2: Create index
    print("\n🔍 Step 2: Creating search index...")
    if not create_or_update_index():
        return
    
    # Step 3: Create indexer
    print("\n⚙️ Step 3: Creating indexer...")
    if not create_or_update_indexer():
        return
    
    # Step 4: Run indexer
    print("\n🏃 Step 4: Running indexer to import data...")
    if not run_indexer():
        return
    
    print("\n⏳ Waiting for indexer to complete...")
    import time
    time.sleep(10)  # Wait 10 seconds
    
    # Step 5: Check status
    print("\n📋 Step 5: Checking indexer status...")
    check_indexer_status()
    
    print("\n🎉 Azure AI Search setup completed!")
    print(f"📍 You can now use the search index '{INDEX_NAME}' to query your product catalog data.")

if __name__ == "__main__":
    main()