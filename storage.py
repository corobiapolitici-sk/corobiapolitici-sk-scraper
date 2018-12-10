from pymongo import MongoClient
from neo4j.v1 import GraphDatabase
from datetime import datetime
import constants as const
import yaml
import logging
import pandas as pd
import utils
import os

class MongoDatabase:
    def __init__(self, conf):
        self.conf = conf
        self.client = MongoClient(**self.conf[const.CONF_MONGO_CLIENT])
        self.name = self.conf[const.CONF_MONGO_DATABASE][const.CONF_MONGO_DATABASE_NAME]
        self.database = self.client[self.name]
        self.log = logging.getLogger("Mongo")
        self.log.info("MongoDatabase initialized with database '%r'.", self.name)

    def close(self):
        self.client.close()

class MongoCollection:
    def __init__(self, db, collection):
        self.db = db
        self.name = collection
        self.collection = self.db.database[self.name]
        self.log = logging.getLogger("Mongo-{}".format(self.name))
        self.log.debug("MongoCollection initialized.")

    def insert(self, data):
        data[const.MONGO_TIMESTAMP] = datetime.now()
        obj = self.collection.insert_one(data)
        self.log.debug("Inserted data with id %r.", obj.inserted_id)

    def insert_batch(self, entries):
        for entry in entries:
            entry[const.MONGO_TIMESTAMP] = datetime.now()
        self.collection.insert_many(entries)
        self.log.debug("Inserted %d entries.", len(entries))

    def update(self, data, keys):
        if isinstance(keys, str):
            keys = [keys]
        for key in keys:
            if key not in data:
                self.log.error("The key %r is not in data.", key)
                return
        query = {key: data[key] for key in keys}
        dups = list(self.collection.find(query))
        if dups:
            if len(dups) > 1:
                self.log.error("There are multiple duplicates of %r with value %r.",
                    str(keys), str([data[key] for key in keys]))
                return
            else:
                self.collection.delete_one(query)
                self.log.debug("Entry with key: value pair %r: %r deleted.", 
                    str(keys), str([data[key] for key in keys]).encode("utf-8")) # TODO: only a hotfix
        else:
            self.log.debug("Nothing to update -- inserting instead.")
        self.insert(data)

    def get(self, query, **kwargs):
        entry = self.collection.find_one(query, **kwargs)
        if entry is None:
            self.log.debug("Query found nothing.")
        else:
            self.log.debug("Query found object %r.", entry["_id"])
        return entry
    
    def get_all(self, query, projections=None):
        entries = list(self.collection.find(query, projections))
        self.log.debug("Query found %d objects.", len(entries))
        return entries

    def get_all_attribute(self, attribute):
        results = self.get_all({}, [attribute])
        return [res[attribute] for res in results if attribute in res]
    
    def exists(self, query):
        return self.get(query) is not None

    def iterate_all(self):
        unique_ids = self.get_all_attribute(const.MONGO_UNIQUE_ID)
        for unique_id in unique_ids:
            yield self.get({const.MONGO_UNIQUE_ID: unique_id})

class Neo4jDatabase:
    def __init__(self, conf):
        self.conf = conf
        self.uri = self.conf[const.CONF_NEO4J_CLIENT][const.CONF_NEO4J_URI]
        self.auth = tuple(self.conf[const.CONF_NEO4J_CLIENT][const.CONF_NEO4J_AUTH])
        self.client = GraphDatabase.driver(self.uri, auth=self.auth)
        self.session = self.client.session() #pylint: disable=E1111
        self.temp_csv = self.conf[const.CONF_NEO4J_TEMP_CSV]
        self.temp_csv_location = os.path.join(
            self.conf[const.CONF_NEO4J_IMPORT_PATH], self.temp_csv)
        self.periodic_commit = self.conf[const.CONF_NEO4J_PERIODIC_COMMIT]
        self.log = logging.getLogger("Neo4j")
        self.log.info("Neo4j database initialized.")
    
    def close(self):
        self.client.close()

    def create_temp_csv(self, cols):
        pd.DataFrame(columns=cols).to_csv(self.temp_csv_location, index=False)
        self.log.info("Temporary csv file created at %r.", self.temp_csv_location)

    def append_temp_csv(self, cols, row):
        entry = {col: utils.date_converter_csv(row[col]) for col in cols}
        pd.DataFrame(entry, columns=cols).to_csv(
            self.temp_csv_location, mode="a", index=False, header=False)

    def batch_append_temp_csv(self, cols, entries):
        entries = [{col: utils.date_converter_csv(entry[col]) for col in cols} 
            for entry in entries]
        pd.DataFrame(entries, columns=cols).to_csv(
            self.temp_csv_location, mode="a", index=False, header=False)


    def create_query(self, cols, entry, specs):
        query = "LOAD CSV WITH HEADERS FROM \"file:///{}\" AS row\n".format(self.temp_csv)
        checknull = "(CASE WHEN {{}} = \"{}\" THEN null ELSE {{}} END)".format(
            const.NEO4J_NULLVALUE)
        def typed(key):
            rowdot = "row.{}".format(key)
            return checknull.format(rowdot, self.type_formatter(entry[key])(rowdot))
        fil = lambda key: "{{{}: {}}}".format(const.MONGO_ID, typed(key))
        if specs[const.NEO4J_OBJECT_TYPE] == const.NEO4J_OBJECT_NODE:
            query += "MERGE (x:{} {})\n".format(specs[const.NEO4J_NODE_NAME], fil(const.MONGO_ID))
        elif specs[const.NEO4J_OBJECT_TYPE] == const.NEO4J_OBJECT_EDGE:
            query += "MATCH (a:{} {})\n".format(
                specs[const.NEO4J_BEGINNING_NAME], fil(const.NEO4J_BEGINNING_ID))
            query += "MATCH (b:{} {})\n".format(
                specs[const.NEO4J_ENDING_NAME], fil(const.NEO4J_ENDING_ID))
            query += "MERGE (a)-[x:{}]-(b)\n".format(specs[const.NEO4J_EDGE_NAME])
        else:
            raise ValueError("Unknown object type {}".format(specs[const.NEO4J_OBJECT_TYPE]))
        for key in entry:
            if key not in [const.MONGO_ID, const.NEO4J_BEGINNING_ID, const.NEO4J_ENDING_ID]:
                query += "SET x.{} = {}\n".format(key, typed(key))
        self.log.info("Query for %r constructed.", specs[const.NEO4J_OBJECT_TYPE])
        self.log.debug("%s", query)
        return query

    def type_formatter(self, obj):
        if isinstance(obj, bool):
            return lambda s: const.NEO4J_BOOLEAN.format(s)
        elif isinstance(obj, int):
            return lambda s: const.NEO4J_INTEGER.format(s)
        elif isinstance(obj, datetime):
            return lambda s: const.NEO4J_DATETIME.format(s)
        elif isinstance(obj, str):
            return lambda s: const.NEO4J_STRING.format(s)
        else:
            raise ValueError("Invalid type {} in neo4j type_formatter".format(type(obj)))

    def import_objects(self, collection, **specs):
        entries = collection.get_all_attribute(const.MONGO_UNIQUE_ID)
        self.log.info("Objects insertion started.")
        for i, unique_id in enumerate(entries):
            entry = collection.get({const.MONGO_UNIQUE_ID: unique_id})
            del entry[const.MONGO_UNIQUE_ID]
            if i == 0:
                cols = list(entry.keys())
                self.create_temp_csv(cols)
                query = self.create_query(cols, entry, specs)
                if len(entries) > self.periodic_commit:
                    query = "USING PERIODIC COMMIT {}\n".format(self.periodic_commit) + query
            self.append_temp_csv(cols, entry)
            self.log.info("Overall insertion progress: %d / %d.", i+1, len(entries))
        self.session.run(query)
        self.log.info("Objects insertion finished!")

    def batch_import_objects(self, collection, **specs):
        all_entries = collection.get_all_attribute(const.MONGO_UNIQUE_ID)
        self.log.info("Batch objects insertion started.")
        unique_ids = []
        for i, unique_id in enumerate(all_entries):
            unique_ids.append(unique_id)
            if i == 0:
                entry = collection.get({const.MONGO_UNIQUE_ID: unique_id})
                del entry[const.MONGO_UNIQUE_ID]
                cols = list(entry.keys())
                self.create_temp_csv(cols)
                query = self.create_query(cols, entry, specs)
                if len(all_entries) > self.periodic_commit:
                    query = "USING PERIODIC COMMIT {}\n".format(self.periodic_commit) + query
            if len(unique_ids) == const.NEO4J_BATCH_INSERT:
                entries = collection.get_all({const.MONGO_UNIQUE_ID: {"$in": unique_ids}})
                self.batch_append_temp_csv(cols, entries)
                self.log.info("Overall batch insertion progress: %d / %d.", i+1, len(all_entries))
                unique_ids = []
        entries = collection.get_all({const.MONGO_UNIQUE_ID: {"$in": unique_ids}})
        self.batch_append_temp_csv(cols, entries)
        self.log.info("Overall batch insertion progress: %d / %d.", i+1, len(all_entries))
        self.log.info("Neo4j insertion started.")
        self.session.run(query)
        if specs[const.NEO4J_OBJECT_TYPE] == const.NEO4J_OBJECT_NODE:
            query = "CREATE INDEX ON :{}({})".format(specs[const.NEO4J_NODE_NAME], const.MONGO_ID)
            self.session.run(query)
            self.log.info("Index on %s created", specs[const.NEO4J_NODE_NAME])
        self.log.info("Objects batch insertion finished!")
