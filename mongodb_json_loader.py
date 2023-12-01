import pymongo
import json

# convert JSON data to Python dict
with open("fighter_data.json", "r") as f:
    fighter_data = json.load(f)

# Convert specific fields to desired types
for fighter in fighter_data:
    fighter['rank'] = int(fighter.get('rank')) if fighter.get('rank') is not None else None
    fighter['champion'] = bool(fighter.get('champion'))
    fighter['win_streak'] = int(fighter.get('win_streak'))
    fighter['fight_record']['win'] = int(fighter['fight_record'].get('win'))
    fighter['fight_record']['loss'] = int(fighter['fight_record'].get('loss'))
    if fighter.get('country') is None:
        fighter['country'] = "Unknown"

# Connect to MongoDB (assuming it's running on localhost)
client = pymongo.MongoClient("mongodb://localhost:27017")
database = client["UFC"]

# Drop the existing 'fighter_data' collection if it exists
if 'fighter_data' in database.list_collection_names():
    database.drop_collection('fighter_data')

# Define the schema using JSON Schema
schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["_id", "name", "country", "weight_class", "rank", "champion", "win_streak", "last_fight_outcome", "fight_record"],
        "properties": {
            "_id": {
                "bsonType": "string"
            },
            "name": {
                "bsonType": "string"
            },
            "country": {
                "bsonType": "string"
            },
            "weight_class": {
                "bsonType": "string"
            },
            "rank": {
                "bsonType": ["int", "null"]
            },
            "champion": {
                "bsonType": "bool"
            },
            "win_streak": {
                "bsonType": "int"
            },
            "last_fight_outcome": {
                "enum": ["win", "loss", "other", "not found"]
            },
            "fight_record": {
                "bsonType": "object",
                "required": ["win", "loss"],
                "properties": {
                    "win": {
                        "bsonType": "int"
                    },
                    "loss": {
                        "bsonType": "int"
                    }
                }
            }
        }
    }
}

collection = database.create_collection('fighter_data', validator=schema)

# Insert each element from the JSON list into MongoDB collection
for item in fighter_data:
    collection.insert_one(item)

# Close MongoDB connection
client.close()
