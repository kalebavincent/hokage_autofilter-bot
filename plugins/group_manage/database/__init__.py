from pymongo import MongoClient
from pymongo.errors import PyMongoError
from motor.motor_asyncio import AsyncIOMotorClient
from info import DATABASE_NAME, DATABASE_URI
import pymongo
import logging
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

mongo_client = AsyncIOMotorClient(DATABASE_URI)
db = mongo_client.wbb


afkusers = db.afkusers
chatb = db.chatbot

myapp = pymongo.MongoClient(DATABASE_URI)
dbx = myapp["AsyncIOMotorCursor"]
federation = dbx['federation']
nm = dbx['Nightmode']

try:
    alita_db_client = MongoClient(DATABASE_URI)
except PyMongoError as f:
    LOGGER.error(f"Error in Mongodb: {f}")
    exit(1)
alita_main_db = alita_db_client[DATABASE_NAME]


class MongoDB:
    """Class for interacting with Bot database."""

    def __init__(self, collection) -> None:
        self.collection = alita_main_db[collection]

    # Insert one entry into collection
    def insert_one(self, document):
        result = self.collection.insert_one(document)
        return repr(result.inserted_id)

    # Find one entry from collection
    def find_one(self, query):
        result = self.collection.find_one(query)
        if result:
            return result
        return False

    # Find entries from collection
    def find_all(self, query=None):
        if query is None:
            query = {}
        return list(self.collection.find(query))

    # Count entries from collection
    def count(self, query=None):
        if query is None:
            query = {}
        return self.collection.count_documents(query)

    # Delete entry/entries from collection
    def delete_one(self, query):
        self.collection.delete_many(query)
        return self.collection.count_documents({})

    # Replace one entry in collection
    def replace(self, query, new_data):
        old = self.collection.find_one(query)
        _id = old["_id"]
        self.collection.replace_one({"_id": _id}, new_data)
        new = self.collection.find_one({"_id": _id})
        return old, new

    # Update one entry from collection
    def update(self, query, update):
        result = self.collection.update_one(query, {"$set": update})
        new_document = self.collection.find_one(query)
        return result.modified_count, new_document

    @staticmethod
    def close():
        return alita_db_client.close()


def __connect_first():
    _ = MongoDB("test")
    LOGGER.info("Initialized Database!\n")


__connect_first()
