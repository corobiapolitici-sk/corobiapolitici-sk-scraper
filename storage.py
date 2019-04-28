# Load external modules.
from datetime import datetime
import logging
from neo4j.v1 import GraphDatabase
import os
import pandas as pd
import yaml

# Load internal modules.
import constants as const
import utils

class MongoCollection:
    def __init__(self, db, collection):
        self.collection = db[collection]
        self.log = logging.getLogger(f'Mongo-{collection}')
        self.log.debug('MongoCollection initialized.')

    def insert(self, data):
        data[const.MONGO_TIMESTAMP] = datetime.now()
        obj = self.collection.insert_one(data)
        self.log.debug(f'Inserted data with id {obj.inserted_id}.')

    def insert_batch(self, entries):
        for entry in entries:
            entry[const.MONGO_TIMESTAMP] = datetime.now()
        self.collection.insert_many(entries)
        self.log.debug(f'Inserted {len(entries)} entries.')

    def update(self, data, keys):
        if isinstance(keys, str):
            keys = [keys]

        query = { key: data[key] for key in keys }
        dups = list(self.collection.find(query))
        if dups:
            if len(dups) > 1:
                self.log.error(f'There are multiple duplicates of {str(keys)} with value {str([data[key] for key in keys])}.')
                return
            else:
                self.collection.delete_one(query)
                self.log.debug(f'Entry with key: value pair {str(keys)}: {str([data[key] for key in keys]).encode("utf-8")} deleted.') # TODO: only a hotfix
        else:
            self.log.debug('Nothing to update -- inserting instead.')
        self.insert(data)

    def get(self, query, **kwargs):
        entry = self.collection.find_one(query, **kwargs)
        if entry is None:
            self.log.debug('Query found nothing.')
        else:
            self.log.debug(f'Query found object {entry["_id"]}.')
        return entry

    def get_all(self, query, projections=None):
        entries = list(self.collection.find(query, projections))
        self.log.debug(f'Query found {len(entries)} objects.')
        return entries

    def get_all_attribute(self, attribute):
        results = self.get_all({}, [attribute])
        return [res[attribute] for res in results if attribute in res]

    def exists(self, query):
        return self.get(query) is not None

    def iterate_all(self):
        unique_ids = self.get_all_attribute('_id')
        for unique_id in unique_ids:
            yield self.get({ '_id': unique_id })

class Neo4jDatabase:
    def __init__(self, conf):
        self.conf = conf
        self.uri = self.conf[const.CONF_NEO4J_CLIENT][const.CONF_NEO4J_URI]
        self.auth = tuple(self.conf[const.CONF_NEO4J_CLIENT][const.CONF_NEO4J_AUTH])
        self.client = GraphDatabase.driver(self.uri, auth=self.auth)
        self.session = self.client.session() #pylint: disable=E1111
        self.temp_csv = self.conf[const.CONF_NEO4J_TEMP_CSV]
        self.temp_csv_location = os.path.join(self.conf[const.CONF_NEO4J_IMPORT_PATH], self.temp_csv)
        self.periodic_commit = self.conf[const.CONF_NEO4J_PERIODIC_COMMIT]
        self.log = logging.getLogger('Neo4j')
        self.log.info('Neo4j database initialized.')

    def close(self):
        self.client.close()

    def create_temp_csv(self, cols):
        pd.DataFrame(columns=cols).to_csv(self.temp_csv_location, index=False)
        self.log.info(f'Temporary csv file created at {self.temp_csv_location}.')

    def append_temp_csv(self, cols, row):
        entry = {col: utils.date_converter_csv(row[col]) for col in cols}
        pd.DataFrame(entry, columns=cols).to_csv(
            self.temp_csv_location, mode='a', index=False, header=False)

    def batch_append_temp_csv(self, cols, entries):
        entries = [{col: utils.date_converter_csv(entry[col]) for col in cols}
            for entry in entries]
        pd.DataFrame(entries, columns=cols).to_csv(
            self.temp_csv_location, mode='a', index=False, header=False)

    def create_query(self, cols, entry, specs):
        query = f'LOAD CSV WITH HEADERS FROM "file:///{self.temp_csv}" AS row\n'
        checknull = f'(CASE WHEN {{}} = "{const.NEO4J_NULLVALUE}" THEN null ELSE {{}} END)'
        def typed(key):
            rowdot = f'row.{key}'
            return checknull.format(rowdot, self.type_formatter(entry[key])(rowdot))
        fil = lambda key: f'{{{const.MONGO_ID}: {typed(key)}}}'
        if specs[const.NEO4J_OBJECT_TYPE] == const.NEO4J_OBJECT_NODE:
            query += f'MERGE (x:{specs[const.NEO4J_NODE_NAME]} {fil(const.MONGO_ID)})\n'
        elif specs[const.NEO4J_OBJECT_TYPE] == const.NEO4J_OBJECT_EDGE:
            query += f'MATCH (a:{specs[const.NEO4J_BEGINNING_NAME]} {fil(const.NEO4J_BEGINNING_ID)})\n'
            query += f'MATCH (b:{specs[const.NEO4J_ENDING_NAME]} {fil(const.NEO4J_ENDING_ID)})\n'
            query += f'MERGE (a)-[x:{specs[const.NEO4J_EDGE_NAME]}]-(b)\n'
        else:
            raise ValueError(f'Unknown object type {specs[const.NEO4J_OBJECT_TYPE]}')
        for key in entry:
            if key not in [const.MONGO_ID, const.NEO4J_BEGINNING_ID, const.NEO4J_ENDING_ID]:
                query += f'SET x.{key} = {typed(key)}\n'
        self.log.info(f'Query for {specs[const.NEO4J_OBJECT_TYPE]} constructed.')
        self.log.debug(str(query))
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
            raise ValueError(f'Invalid type {type(obj)} in neo4j type_formatter')

    def import_objects(self, collection, **specs):
        entries = collection.get_all_attribute(const.MONGO_UNIQUE_ID)
        self.log.info('Objects insertion started.')
        for i, unique_id in enumerate(entries):
            entry = collection.get({const.MONGO_UNIQUE_ID: unique_id})
            del entry[const.MONGO_UNIQUE_ID]
            if i == 0:
                cols = list(entry.keys())
                self.create_temp_csv(cols)
                query = self.create_query(cols, entry, specs)
                if len(entries) > self.periodic_commit:
                    query = f'USING PERIODIC COMMIT {self.periodic_commit}\n' + query
            self.append_temp_csv(cols, entry)
            self.log.info(f'Overall insertion progress: {i + 1} / {len(entries)}.')
        self.session.run(query)
        self.log.info('Objects insertion finished!')

    def batch_import_objects(self, collection, **specs):
        all_entries = collection.get_all_attribute(const.MONGO_UNIQUE_ID)
        self.log.info('Batch objects insertion started.')
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
                    query = f'USING PERIODIC COMMIT {self.periodic_commit}\n' + query
            if len(unique_ids) == const.NEO4J_BATCH_INSERT:
                entries = collection.get_all({const.MONGO_UNIQUE_ID: {'$in': unique_ids}})
                self.batch_append_temp_csv(cols, entries)
                self.log.info(f'Overall batch insertion progress: {i + 1} / {len(all_entries)}.')
                unique_ids = []
        entries = collection.get_all({const.MONGO_UNIQUE_ID: {'$in': unique_ids}})
        self.batch_append_temp_csv(cols, entries)
        self.log.info(f'Overall batch insertion progress: {i + 1} / {len(all_entries)}.')
        self.log.info('Neo4j insertion started.')
        self.session.run(query)
        if specs[const.NEO4J_OBJECT_TYPE] == const.NEO4J_OBJECT_NODE:
            query = f'CREATE INDEX ON :{specs[const.NEO4J_NODE_NAME]}({const.MONGO_ID})'
            self.session.run(query)
            self.log.info(f'Index on {specs[const.NEO4J_NODE_NAME]} created')
        self.log.info('Objects batch insertion finished!')
