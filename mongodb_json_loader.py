import pymongo
import json

# convert JSON data to Python dict
with open("fighter_data.json", "r") as f:
    fighter_data = json.load(f)

# Connect to MongoDB (assuming it's running on localhost)
client = pymongo.MongoClient("mongodb://localhost:27017")
database = client["UFC"]
collection = database["fighter_data"]

# Insert each element from the JSON list into MongoDB collection
for item in fighter_data:
    collection.insert_one(item)

# Close MongoDB connection
client.close()
