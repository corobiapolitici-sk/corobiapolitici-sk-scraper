from pymongo import MongoClient
from datetime import datetime
import constants as const
import yaml
import logging

class MongoDatabase:
    def __init__(self, conf):
        self.conf = conf
        self.client = MongoClient(**self.conf[const.CONF_MONGO_CLIENT])
        self.name = self.conf[const.CONF_MONGO_DATABASE][const.CONF_MONGO_DATABASE_NAME]
        self.database = self.client[self.name]
        self.log = logging.getLogger("Mongo")
        logging.basicConfig(**self.conf[const.LOGGING])  # TODO: to main
        self.log.info("MongoDatabase initialized with database '%s'.", self.name)

class MongoCollection:
    def __init__(self, db, collection):
        self.db = db
        self.name = collection
        self.collection = self.db.database[self.name]
        self.log = logging.getLogger("Mongo-{}".format(self.name))
        self.log.info("MongoCollection initialized.")

    def insert(self, data):
        data[const.MONGO_TIMESTAMP] = datetime.now()
        obj = self.collection.insert_one(data)
        self.log.info("Inserted data with id %s.", obj.inserted_id)

    def update(self, data, key):
        if key not in data:
            self.log.error("The key %s is not in data.", key)
            return
        query = {key: data[key]}
        dups = list(self.collection.find(query))
        if dups:
            if len(dups) > 1:
                self.log.error("There are multiple duplicates of %s with value %s.",
                    key, str(data[key]))
                return
            else:
                self.collection.delete_one(query)
                self.log.info("Entry with key: value pair %s: %s deleted.", key, str(data[key]))
        else:
            self.log.info("Nothing to update -- inserting instead.")
        self.insert(data)

    def get(self, query, projections=None):
        entry = self.collection.find_one(query, projections)
        if entry is None:
            self.log.info("Query found nothing.")
        else:
            self.log.info("Query found object %s.", entry["_id"])
        return entry
    
    def get_all(self, query, projections=None):
        entries = list(self.collection.find(query, projections))
        self.log.info("Query found %d objects.", len(entries))
        return entries
    
    def exists(self, query):
        return self.get(query) is not None
