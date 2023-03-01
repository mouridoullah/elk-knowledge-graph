import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["dbDocuments"]
collection = db["test"]

delete_result = collection.delete_many({})

print(delete_result.deleted_count, "documents deleted.")
