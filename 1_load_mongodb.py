import json
import pymongo
import os

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["mamionmiam"]

data_dir = "mamionmiam/mamionmiam"
files = [
    "shops.json",
    "clients.json",
    "parrainages.json",
    "entreprises.json",
    "achats.json",
    "produits.json"
]

def load_data():
    for file in files:
        collection_name = file.split('.')[0]
        file_path = os.path.join(data_dir, file)
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                db[collection_name].drop() # Clear collection before loading
                
                if isinstance(data, list) and len(data) > 0:
                    db[collection_name].insert_many(data)
                    print(f"Loaded {len(data)} items into {collection_name}")
                elif isinstance(data, dict):
                    db[collection_name].insert_one(data)
                    print(f"Loaded 1 item into {collection_name}")
                else:
                    print(f"No data loaded for {collection_name} or format not recognized")
        else:
            print(f"File not found: {file_path}")

if __name__ == "__main__":
    load_data()
    print("Data loaded successfully to MongoDB.")
