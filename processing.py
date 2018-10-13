import logging
import numpy as np

import storage
import constants as const
import utils
from datetime import datetime

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
        source_collection = utils.get_collection(
            const.CONF_MONGO_POSLANEC, self.conf, const.CONF_MONGO_PARSED, self.db)
        for entry in source_collection.iterate_all():
            del entry[const.POSLANEC_CLENSTVO]
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

class NodesVybor(Nodes):
    def __init__(self, *args):
        super().__init__(*args)
        self.node_name = const.NODE_NAME_VYBOR

    def entry_generator(self):
        source_collection = utils.get_collection(
            const.CONF_MONGO_POSLANEC, self.conf, const.CONF_MONGO_PARSED, self.db)
        orgs = set()
        for entry in source_collection.iterate_all():
            for org in entry[const.POSLANEC_CLENSTVO]:
                if const.NODE_NAME_VYBOR.lower() in org.lower():
                    orgs.add(org)
        for org in orgs:
            yield {const.MONGO_ID: org}

class NodesDelegacia(Nodes):
    def __init__(self, *args):
        super().__init__(*args)
        self.node_name = const.NODE_NAME_DELEGACIA

    def entry_generator(self):
        source_collection = utils.get_collection(
            const.CONF_MONGO_POSLANEC, self.conf, const.CONF_MONGO_PARSED, self.db)
        orgs = set()
        for entry in source_collection.iterate_all():
            for org in entry[const.POSLANEC_CLENSTVO]:
                if const.NODE_NAME_DELEGACIA.lower() in org.lower():
                    orgs.add(org)
        for org in orgs:
            yield {const.MONGO_ID: org}

class NodesZakon(Nodes):
    def __init__(self, *args):
        super().__init__(*args)
        self.node_name = const.NODE_NAME_ZAKON

    def entry_generator(self):
        source_collection = utils.get_collection(
            const.CONF_MONGO_ZAKON, self.conf, const.CONF_MONGO_PARSED, self.db)
        fields = [
            const.MONGO_ID,
            const.MONGO_TIMESTAMP,
            const.ZAKON_STAV,
            const.ZAKON_VYSLEDOK,
            const.ZAKON_DRUH,
            const.ZAKON_NAZOV,
            const.MONGO_URL,
            const.MONGO_UNIQUE_ID,
            const.ZAKON_DATUM_DORUCENIA
        ]
        for entry in source_collection.iterate_all():
            yield {
                field: entry[field] if field in entry else const.NEO4J_NULLVALUE 
                for field in fields
            }

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
            const.CONF_MONGO_HLASOVANIE, self.conf, const.CONF_MONGO_PARSED, self.db)
        last_entry = source_collection.get({}, projection=[const.HLASOVANIE_INDIVIDUALNE],
            sort=[(const.MONGO_ID, -1)])
        aktivni_ids = [int(i) for i in last_entry[const.HLASOVANIE_INDIVIDUALNE].keys()]
        source_collection = utils.get_collection(
            const.CONF_MONGO_POSLANEC, self.conf, const.CONF_MONGO_PARSED, self.db
        )
        for entry in source_collection.iterate_all():
            if entry[const.MONGO_ID] in aktivni_ids:
                klub = const.KLUB_NEZARADENI
                typ = const.CLEN_CLEN
                for org in entry[const.POSLANEC_CLENSTVO]:
                    if org in const.KLUB_DICT:
                        klub = const.KLUB_DICT[org]
                        typ = const.CLEN_TYP_DICT[entry[const.POSLANEC_CLENSTVO][org]]
                        break
                result = {
                    const.NEO4J_BEGINNING_ID: int(entry[const.MONGO_ID]),
                    const.NEO4J_ENDING_ID: klub,
                    const.CLEN_TYP: typ
                }
            yield result


class EdgesPoslanecVyborClen(Edges):
    def __init__(self, *args):
        super().__init__(*args)
        self.edge_name = const.EDGE_NAME_CLEN
        self.beginning_name = const.NODE_NAME_POSLANEC
        self.ending_name = const.NODE_NAME_VYBOR

    def entry_generator(self):
        source_collection = utils.get_collection(
            const.CONF_MONGO_POSLANEC, self.conf, const.CONF_MONGO_PARSED, self.db
        )
        for entry in source_collection.iterate_all():
            for org, typ in entry[const.POSLANEC_CLENSTVO].items():
                if const.NODE_NAME_VYBOR.lower() in org.lower():
                    result = {
                        const.NEO4J_BEGINNING_ID: entry[const.MONGO_ID],
                        const.NEO4J_ENDING_ID: org,
                        const.CLEN_TYP: const.CLEN_TYP_DICT[typ]
                    }
                    yield result


class EdgesPoslanecDelegaciaClen(Edges):
    def __init__(self, *args):
        super().__init__(*args)
        self.edge_name = const.EDGE_NAME_CLEN
        self.beginning_name = const.NODE_NAME_POSLANEC
        self.ending_name = const.NODE_NAME_DELEGACIA

    def entry_generator(self):
        source_collection = utils.get_collection(
            const.CONF_MONGO_POSLANEC, self.conf, const.CONF_MONGO_PARSED, self.db
        )
        for entry in source_collection.iterate_all():
            for org, typ in entry[const.POSLANEC_CLENSTVO].items():
                if const.NODE_NAME_DELEGACIA.lower() in org.lower():
                    result = {
                        const.NEO4J_BEGINNING_ID: entry[const.MONGO_ID],
                        const.NEO4J_ENDING_ID: org,
                        const.CLEN_TYP: const.CLEN_TYP_DICT[typ]
                    }
                    yield result

class EdgesPoslanecHlasovanieHlasoval(Edges):
    def __init__(self, *args):
        super().__init__(*args)
        self.edge_name = const.EDGE_NAME_HLASOVAL
        self.beginning_name = const.NODE_NAME_POSLANEC
        self.ending_name = const.NODE_NAME_HLASOVANIE

    def entry_generator(self):
        source_collection = utils.get_collection(
            const.CONF_MONGO_HLASOVANIE, self.conf, const.CONF_MONGO_PARSED, self.db
        )
        for entry in source_collection.iterate_all():
            for poslanec_id, poslanec in entry[const.HLASOVANIE_INDIVIDUALNE].items():
                hlas = {
                    const.NEO4J_BEGINNING_ID: int(poslanec_id),
                    const.NEO4J_ENDING_ID: entry[const.MONGO_ID],
                    const.HLASOVAL_HLAS: const.HLASOVAL_HLAS_DICT[poslanec[const.HLASOVANIE_HLAS]],
                    const.HLASOVAL_KLUB: utils.parse_klub(poslanec[const.HLASOVANIE_KLUB])
                }
                yield hlas

class EdgesVyborZakonNavrhnuty(Edges):
    def __init__(self, *args):
        super().__init__(*args)
        self.edge_name = const.EDGE_NAME_NAVHRNUTY
        self.beginning_name = const.NODE_NAME_VYBOR
        self.ending_name = const.NODE_NAME_ZAKON

    def entry_generator(self):
        vybory = [
            entry[const.MONGO_ID] 
            for entry in storage.MongoCollection(self.db, "nodes_vybor").iterate_all()
        ]
        source_collection = utils.get_collection(
            const.CONF_MONGO_ZAKON, self.conf, const.CONF_MONGO_PARSED, self.db
        )
        def result_form(entry, vybor, lehota):
            return  {
                const.NEO4J_BEGINNING_ID: vybor,
                const.NEO4J_ENDING_ID: entry[const.MONGO_ID],
                const.NAVRHNUTY_LEHOTA: lehota
            }
        for entry in source_collection.iterate_all():
            if const.ZAKON_ROZHODNUTIE_VYBORY in entry:
                sprava = entry[const.ZAKON_ROZHODNUTIE_VYBORY]
                if sprava == "":
                    break
                lehota = self.get_lehota(sprava)
                for vybor in vybory:
                    flag = False
                    if vybor in sprava:
                        result = result_form(entry, vybor, lehota)
                        result[const.NAVRHNUTY_TYP] = const.NAVRHNUTY_DOPLNUJUCI
                        flag = True
                    if vybor in entry[const.ZAKON_ROZHODNUTIE_GESTORSKY]:
                        result = result_form(entry, vybor, lehota)
                        result[const.NAVRHNUTY_TYP] = const.NAVRHNUTY_GESTORSKY
                        flag = True
                    if flag:
                        yield result
    
    def get_lehota(self, sprava):
        datum = sprava.split("prerokovanie ")[-1].strip()
        if datum == sprava or datum == "ihneď.":
            return const.NEO4J_NULLVALUE
        else:
            return datetime.strptime(datum, "%d. %m. %Y.")

class EdgesVyborZakonGestorsky(Edges):
    def __init__(self, *args):
        super().__init__(*args)
        self.edge_name = const.EDGE_NAME_GESTORSKY
        self.beginning_name = const.NODE_NAME_VYBOR
        self.ending_name = const.NODE_NAME_ZAKON

    def entry_generator(self):
        source_collection = utils.get_collection(
            const.CONF_MONGO_ZAKON, self.conf, const.CONF_MONGO_PARSED, self.db
        )
        for entry in source_collection.iterate_all():
            if const.ZAKON_GESTORSKY in entry:
                yield {
                    const.NEO4J_BEGINNING_ID: entry[const.ZAKON_GESTORSKY],
                    const.NEO4J_ENDING_ID: entry[const.MONGO_ID]
                }