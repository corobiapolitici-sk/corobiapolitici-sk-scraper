import logging
import numpy as np

import storage
import constants as const
import utils

class Processing:
    def __init__(self, db, conf):
        self.db = db
        self.conf = conf
        self.name = str(self.__class__).split("'")[1]
        self.target_name = utils.camel2snake(self.name.split(".")[-1])
        self.target_collection = storage.MongoCollection(self.db, self.target_name)
        self.log = logging.getLogger(self.name)
        

    def entry_generator(self):
        pass

    def process_all(self):
        for entry in self.entry_generator():
            if const.NEO4J_OBJECT_NODE in self.target_name:
                keys = const.MONGO_ID
            elif const.NEO4J_OBJECT_EDGE in self.target_name:
                keys = [const.NEO4J_BEGINNING_ID, const.NEO4J_ENDING_ID]
            else:
                raise ValueError("Unsupported target name {}".format(self.target_name))
            self.target_collection.update(entry, keys)
            self.log.info("Entry inserted into collection %r", self.target_name)

    def import_all_to_neo(self, **kwargs):
        neo = storage.Neo4jDatabase(self.conf[const.CONF_NEO4J])
        neo.import_objects(self.target_collection, **kwargs)
        neo.close()

    def process_and_store_all(self, **kwargs):
        self.process_all()
        self.import_all_to_neo(**kwargs)

#########
# NODES #
#########

class Nodes(Processing):
    def __init__(self, *args):
        super().__init__(*args)
        self.node_name = ""

    def import_all_to_neo(self):
        super().import_all_to_neo(object_type=const.NEO4J_OBJECT_NODE, node_name=self.node_name)


class NodesHlasovanie(Nodes):
    def __init__(self, *args):
        super().__init__(*args)
        self.node_name = const.NODE_NAME_HLASOVANIE

    def entry_generator(self):
        source_collection = utils.get_collection(
            const.CONF_MONGO_HLASOVANIE, self.conf, const.CONF_MONGO_PARSED, self.db)
        for entry in source_collection.iterate_all():
            del entry[const.MONGO_TIMESTAMP]
            del entry[const.HLASOVANIE_INDIVIDUALNE]
            yield entry


class NodesPoslanec(Nodes):
    def __init__(self, *args):
        super().__init__(*args)
        self.node_name = const.NODE_NAME_POSLANEC

    def entry_generator(self):
        poslanci = {}
        source_collection = utils.get_collection(
            const.CONF_MONGO_HLASOVANIE, self.conf, const.CONF_MONGO_PARSED, self.db)
        for entry in source_collection.iterate_all():
            for poslanec_id, stats in entry[const.HLASOVANIE_INDIVIDUALNE].items():
                if poslanec_id not in poslanci:
                    mena = stats[const.HLASOVANIE_CELE_MENO].split(",")
                    priezvisko, meno = [s.strip() for s in mena]
                    poslanci[poslanec_id] = {const.POSLANEC_MENO: meno,
                        const.POSLANEC_PRIEZVISKO: priezvisko}
        for poslanec_id, entry in poslanci.items():
            entry[const.MONGO_ID] = int(poslanec_id)
            yield entry

class NodesKlub(Nodes):
    def __init__(self, *args):
        super().__init__(*args)
        self.node_name = const.NODE_NAME_KLUB

    def entry_generator(self):
        source_collection = utils.get_collection(
            const.CONF_MONGO_HLASOVANIE, self.conf, const.CONF_MONGO_PARSED, self.db
        )
        last_entry = source_collection.get({}, projection=[const.HLASOVANIE_INDIVIDUALNE],
            sort=[(const.MONGO_ID, -1)])
        hlasy = last_entry[const.HLASOVANIE_INDIVIDUALNE].values()
        kluby = [value[const.HLASOVANIE_KLUB] for value in hlasy] 
        values, counts = np.unique(kluby, return_counts=True)
        for val, count in zip(values, counts):
            val = utils.parse_klub(val)
            entry = {const.MONGO_ID: val, const.KLUB_POCET: int(count)}
            yield entry

#########
# EDGES #
#########

class Edges(Processing):
    def __init__(self, *args):
        super().__init__(*args)
        self.edge_name = ""
        self.beginning_name = ""
        self.ending_name = ""

    def import_all_to_neo(self):
        super().import_all_to_neo(
            object_type=const.NEO4J_OBJECT_EDGE,
            edge_name=self.edge_name,
            beginning_name=self.beginning_name,
            ending_name=self.ending_name)

class EdgesPoslanecKlubClen(Edges):
    def __init__(self, *args):
        super().__init__(*args)
        self.edge_name = const.EDGE_NAME_CLEN
        self.beginning_name = const.NODE_NAME_POSLANEC
        self.ending_name = const.NODE_NAME_KLUB

    def entry_generator(self):
        source_collection = utils.get_collection(
            const.CONF_MONGO_HLASOVANIE, self.conf, const.CONF_MONGO_PARSED, self.db
        )
        poslanci = {}
        for entry in source_collection.iterate_all():
            for poslanec_id in entry[const.HLASOVANIE_INDIVIDUALNE]:
                if poslanec_id in poslanci:
                    if poslanci[poslanec_id][const.CLEN_NAPOSLEDY] > entry[const.HLASOVANIE_CAS]:
                        continue
                values = {
                    const.NEO4J_BEGINNING_ID: int(poslanec_id),
                    const.NEO4J_ENDING_ID: utils.parse_klub(entry[const.HLASOVANIE_INDIVIDUALNE][
                        poslanec_id][const.HLASOVANIE_KLUB]),
                    const.CLEN_NAPOSLEDY: entry[const.HLASOVANIE_CAS]
                }
                poslanci[poslanec_id] = values
        for entry in poslanci.values():
            yield entry
        


