import logging
import numpy as np
import pandas as pd

import storage
import constants as const
import utils
from datetime import datetime, timedelta

class Processing:
    def __init__(self, db, conf):
        self.db = db
        self.conf = conf
        self.name = str(self.__class__).split("'")[1]
        self.target_name = utils.camel2snake(self.name.split(".")[-1])
        self.target_collection = storage.MongoCollection(self.db, self.target_name)
        self.log = logging.getLogger(self.name)
        self.batch_process = True

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

    def batch_process_all(self):
        self.target_collection.collection.delete_many({})
        self.log.info("Deleted all entries in collection %s", self.target_name)
        entries_stack = []
        for entry in self.entry_generator():
            entries_stack.append(entry)
            if len(entries_stack) == const.MONGO_BATCH_INSERT:
                self.target_collection.insert_batch(entries_stack)
                self.log.info("Batch inserted into collection %r", self.target_name)
                entries_stack = []
        self.target_collection.insert_batch(entries_stack)
        self.log.info("Batch inserted into collection %r", self.target_name)

    def import_all_to_neo(self, **kwargs):
        neo = storage.Neo4jDatabase(self.conf[const.CONF_NEO4J])
        if self.batch_process:
            neo.batch_import_objects(self.target_collection, **kwargs)
        else:
            neo.import_objects(self.target_collection, **kwargs)
        neo.close()

    def process_and_store_all(self, **kwargs):
        if self.batch_process:
            self.batch_process_all()
        else:
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
                if const.POSLANEC_VYBOR.lower() in org.lower():
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
                if const.POSLANEC_DELEGACIA.lower() in org.lower():
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

class NodesSpektrum(Nodes):
    def __init__(self, *args):
        super().__init__(*args)
        self.node_name = const.NODE_NAME_SPEKTRUM

    def entry_generator(self):
        yield {const.MONGO_ID: const.SPEKTRUM_OPOZICIA}
        yield {const.MONGO_ID: const.SPEKTRUM_KOALICIA}

class NodesZmena(Nodes):
    def __init__(self, *args):
        super().__init__(*args)
        self.node_name = const.NODE_NAME_ZMENA

    def entry_generator(self):
        source_collection = utils.get_collection(
            const.CONF_MONGO_ZMENA, self.conf, const.CONF_MONGO_PARSED, self.db)
        for entry in source_collection.iterate_all():
            entry.pop(const.ZMENA_PODPISANI, None)
            entry.pop(const.ZMENA_DALSI, None)
            entry.pop(const.ZMENA_PREDKLADATEL)
            yield entry

class NodesRozprava(Nodes):
    def __init__(self, *args):
        super().__init__(*args)
        self.node_name = const.NODE_NAME_ROZPRAVA

    def entry_generator(self):
        source_collection = utils.get_collection(
            const.CONF_MONGO_ROZPRAVA, self.conf, const.CONF_MONGO_PARSED, self.db)
        pop_fields = [
            const.ROZPRAVA_TLAC, const.ROZPRAVA_POSLANEC_ID, const.ROZPRAVA_POSLANEC_PRIEZVISKO,
            const.ROZPRAVA_POSLANEC_MENO, const.ROZPRAVA_POSLANEC_KLUB,
            const.ROZPRAVA_POSLANEC_TYP]
        include_fields = [const.MONGO_TIMESTAMP, const.MONGO_URL]
        for entry in source_collection.iterate_all():
            for vystupenie in entry[const.ROZPRAVA_VYSTUPENIA]:
                for field in pop_fields:
                    vystupenie.pop(field, None)
                for field in include_fields:
                    vystupenie[field] = entry[field]
                vystupenie[const.ROZPRAVA_DLZKA] = self.compute_dlzka_vystupenia(
                    vystupenie[const.ROZPRAVA_CAS_ZACIATOK], vystupenie[const.ROZPRAVA_CAS_KONIEC]
                )
                yield vystupenie

    @staticmethod
    def compute_dlzka_vystupenia(zaciatok, koniec):
        dlzka = (koniec - zaciatok).total_seconds()
        if dlzka < 0:
            if -dlzka > timedelta(hours=23).total_seconds():  # vystupenie over midnight
                dlzka += timedelta(days=1).total_seconds()  # end is on the next day
            else:
                dlzka = 0  # some mistake
        return int(dlzka)

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
                if const.POSLANEC_VYBOR.lower() in org.lower():
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
                if const.POSLANEC_DELEGACIA.lower() in org.lower():
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
        self.edge_name = const.EDGE_NAME_NAVRHNUTY
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

class EdgesKlubSpektrumClen(Edges):
    def __init__(self, *args):
        super().__init__(*args)
        self.edge_name = const.EDGE_NAME_CLEN
        self.beginning_name = const.NODE_NAME_KLUB
        self.ending_name = const.NODE_NAME_SPEKTRUM

    def entry_generator(self):
        for klub, spektrum in const.SPEKTRUM_CLEN.items():
            yield {
                const.NEO4J_BEGINNING_ID: klub,
                const.NEO4J_ENDING_ID: spektrum
            }

class EdgesPoslanecZakonNavrhol(Edges):
    def __init__(self, *args):
        super().__init__(*args)
        self.edge_name = const.EDGE_NAME_NAVRHOL
        self.beginning_name = const.NODE_NAME_POSLANEC
        self.ending_name = const.NODE_NAME_ZAKON

    def entry_generator(self):
        source_collection = utils.get_collection(
            const.CONF_MONGO_LEGISLATIVNAINICIATIVA,
            self.conf, const.CONF_MONGO_PARSED, self.db
        )
        for entry in source_collection.iterate_all():
            for zakon_id in entry.get(const.PREDLOZILZAKON_LIST, {}):
                yield {
                    const.NEO4J_BEGINNING_ID: entry[const.MONGO_ID],
                    const.NEO4J_ENDING_ID: int(zakon_id)
                }

class EdgesPoslanecKlubBolClenom(Edges):
    def __init__(self, *args):
        super().__init__(*args)
        self.edge_name = const.EDGE_NAME_BOL_CLEN
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

class EdgesSpektrumZakonNavrhol(Edges):
    def __init__(self, *args):
        super().__init__(*args)
        self.edge_name = const.EDGE_NAME_NAVRHOL
        self.beginning_name = const.NODE_NAME_SPEKTRUM
        self.ending_name = const.NODE_NAME_ZAKON

    def entry_generator(self):
        source_collection = utils.get_collection(
            const.CONF_MONGO_ZAKON, self.conf, const.CONF_MONGO_PARSED, self.db
        )
        col_navrh = storage.MongoCollection(self.db, "edges_poslanec_zakon_navrhol") # TODO: fix collection naming
        col_klub = storage.MongoCollection(self.db, "edges_poslanec_klub_bol_clenom")
        col_spektrum = storage.MongoCollection(self.db, "edges_klub_spektrum_clen")
        for entry in source_collection.iterate_all():
            if const.ZAKON_NAVRHOVATEL not in entry:
                continue
            navrhovatel = entry[const.ZAKON_NAVRHOVATEL]
            zakon_id = entry[const.MONGO_ID]
            if const.NAVRHOL_VLADA.lower() in navrhovatel.lower():
                yield {
                    const.NEO4J_BEGINNING_ID: const.SPEKTRUM_KOALICIA,
                    const.NEO4J_ENDING_ID: zakon_id,
                    const.NAVRHOL_NAVRHOVATEL: navrhovatel
                }
            elif const.NAVRHOL_POSLANCI.lower() in navrhovatel.lower():
                poslanci = [
                    navrh[const.NEO4J_BEGINNING_ID]
                    for navrh in col_navrh.get_all({const.NEO4J_ENDING_ID : entry[const.MONGO_ID]})
                ]
                if not poslanci:
                    continue
                kluby = [
                    col_klub.get({const.NEO4J_BEGINNING_ID: poslanec_id})[const.NEO4J_ENDING_ID]
                    for poslanec_id in poslanci
                ]
                spektrum = [
                    col_spektrum.get({const.NEO4J_BEGINNING_ID: klub})[const.NEO4J_ENDING_ID]
                    for klub in kluby
                ]
                result = {
                    const.NEO4J_ENDING_ID: zakon_id,
                    const.NAVRHOL_NAVRHOVATEL: const.NAVRHOL_POSLANCI
                }
                if spektrum.count(const.SPEKTRUM_KOALICIA) > spektrum.count(const.SPEKTRUM_OPOZICIA):
                    result[const.NEO4J_BEGINNING_ID] = const.SPEKTRUM_KOALICIA
                else:
                    result[const.NEO4J_BEGINNING_ID] = const.SPEKTRUM_OPOZICIA
                yield result

class EdgesHlasovanieZakonHlasovaloO(Edges):
    def __init__(self, *args):
        super().__init__(*args)
        self.edge_name = const.EDGE_NAME_HLASOVALO_O
        self.beginning_name = const.NODE_NAME_HLASOVANIE
        self.ending_name = const.NODE_NAME_ZAKON

    def entry_generator(self):
        source_collection = utils.get_collection(
            const.CONF_MONGO_HLASOVANIETLAC, self.conf, const.CONF_MONGO_PARSED, self.db
        )
        for entry in source_collection.iterate_all():
            for hlasovanie_id in entry.get(const.HLASOVANIETLAC_LIST, {}):
                yield {
                    const.NEO4J_BEGINNING_ID: int(hlasovanie_id),
                    const.NEO4J_ENDING_ID: entry[const.MONGO_ID]
                }

class EdgesPoslanecZmenaNavrhol(Edges):
    def __init__(self, *args):
        super().__init__(*args)
        self.edge_name = const.EDGE_NAME_NAVRHOL
        self.beginning_name = const.NODE_NAME_POSLANEC
        self.ending_name = const.NODE_NAME_ZMENA

    def entry_generator(self):
        source_collection = utils.get_collection(
            const.CONF_MONGO_ZMENA, self.conf, const.CONF_MONGO_PARSED, self.db
        )
        for entry in source_collection.iterate_all():
            yield {
                const.NEO4J_BEGINNING_ID: utils.get_poslanec_id(
                    self.db, entry[const.ZMENA_PREDKLADATEL]),
                const.NEO4J_ENDING_ID: entry[const.MONGO_ID],
                const.NAVRHOL_NAVRHOVATEL: const.NAVRHOL_HLAVNY
            }
            for poslanec in entry.get(const.ZMENA_DALSI, []):
                yield {
                    const.NEO4J_BEGINNING_ID: utils.get_poslanec_id(self.db, poslanec),
                    const.NEO4J_ENDING_ID: entry[const.MONGO_ID],
                    const.NAVRHOL_NAVRHOVATEL: const.NAVRHOL_DALSI
                }

class EdgesPoslanecZmenaPodpisal(Edges):
    def __init__(self, *args):
        super().__init__(*args)
        self.edge_name = const.EDGE_NAME_PODPISAL
        self.beginning_name = const.NODE_NAME_POSLANEC
        self.ending_name = const.NODE_NAME_ZMENA

    def entry_generator(self):
        source_collection = utils.get_collection(
            const.CONF_MONGO_ZMENA, self.conf, const.CONF_MONGO_PARSED, self.db
        )
        for entry in source_collection.iterate_all():
            for poslanec in entry.get(const.ZMENA_PODPISANI, []):
                yield {
                    const.NEO4J_BEGINNING_ID: utils.get_poslanec_id(self.db, poslanec),
                    const.NEO4J_ENDING_ID: entry[const.MONGO_ID]
                }

class EdgesZmenaZakonNavrhnuta(Edges):
    def __init__(self, *args):
        super().__init__(*args)
        self.edge_name = const.EDGE_NAME_NAVRHNUTA
        self.beginning_name = const.NODE_NAME_ZMENA
        self.ending_name = const.NODE_NAME_ZAKON

    def entry_generator(self):
        source_collection = utils.get_collection(
            const.CONF_MONGO_ZAKON, self.conf, const.CONF_MONGO_PARSED, self.db
        )
        for entry in source_collection.iterate_all():
            for zmena_id in entry.get(const.ZAKON_ZMENY, {}):
                yield {
                    const.NEO4J_BEGINNING_ID: int(zmena_id),
                    const.NEO4J_ENDING_ID: entry[const.MONGO_ID]
                }

class EdgesHlasovanieZmenaHlasovaloO(Edges):
    def __init__(self, *args):
        super().__init__(*args)
        self.edge_name = const.EDGE_NAME_HLASOVALO_O
        self.beginning_name = const.NODE_NAME_HLASOVANIE
        self.ending_name = const.NODE_NAME_ZMENA

    def entry_generator(self):
        col_zakon = utils.get_collection(
            const.CONF_MONGO_ZAKON, self.conf, const.CONF_MONGO_PARSED, self.db
        )
        col_tlac = utils.get_collection(
            const.CONF_MONGO_HLASOVANIETLAC, self.conf, const.CONF_MONGO_PARSED, self.db
        )
        for entry in col_zakon.iterate_all():
            zakon = col_tlac.get({const.MONGO_ID: entry[const.MONGO_ID]})
            hlasovania = zakon.get(const.HLASOVANIETLAC_LIST, {})
            zmeny = entry.get(const.ZAKON_ZMENY, {})
            ids = sorted(zmeny.keys())
            names = [zmeny[i][const.ZAKON_ZMENY_PREDKLADATEL].split(",")[0] for i in ids]
            hlas_text = pd.Series({
                key: value[const.HLASOVANIE_NAZOV].split("Hlasovanie")[-1]
                for key, value in hlasovania.items()
                if "druhé čítanie" in value[const.HLASOVANIE_NAZOV]
            })
            if len(hlas_text) == 0:
                continue
            counts = [0] * len(ids)
            for j, name in enumerate(names):
                if names.count(name) > 1:
                    counts[j] = names[:j+1].count(name)
            for j, i in enumerate(ids):
                hlas_name = hlas_text[hlas_text.str.contains(names[j][:-1])]
                if counts[j] > 0:
                    hlas_name = hlas_name[hlas_name.str.contains("{}. návrh".format(counts[j]))]
                for id_hlas, text in hlas_name.items():
                    if not "dopracovanie" in text and not "preložiť" in text:
                        yield {
                            const.NEO4J_BEGINNING_ID: int(id_hlas),
                            const.NEO4J_ENDING_ID: int(i)
                        }

class EdgesPoslanecRozpravaVystupil(Edges):
    def __init__(self, *args):
        super().__init__(*args)
        self.edge_name = const.EDGE_NAME_VYSTUPIL
        self.beginning_name = const.NODE_NAME_POSLANEC
        self.ending_name = const.NODE_NAME_ROZPRAVA

    def entry_generator(self):
        source_collection = utils.get_collection(
            const.CONF_MONGO_ROZPRAVA, self.conf, const.CONF_MONGO_PARSED, self.db
        )
        for entry in source_collection.iterate_all():
            for vystupenie in entry[const.ROZPRAVA_VYSTUPENIA]:
                klub = vystupenie[const.ROZPRAVA_POSLANEC_KLUB]
                klub = const.KLUB_DICT.get("Klub " + klub, const.NEO4J_NULLVALUE)
                yield {
                    const.NEO4J_BEGINNING_ID: entry[const.MONGO_ID],
                    const.NEO4J_ENDING_ID: vystupenie[const.MONGO_ID],
                    const.ROZPRAVA_POSLANEC_KLUB: klub,
                    const.ROZPRAVA_POSLANEC_TYP: vystupenie[const.ROZPRAVA_POSLANEC_TYP]
                }

class EdgesRozpravaZakonTykalaSa(Edges):
    def __init__(self, *args):
        super().__init__(*args)
        self.edge_name = const.EDGE_NAME_TYKALA_SA
        self.beginning_name = const.NODE_NAME_ROZPRAVA
        self.ending_name = const.NODE_NAME_ZAKON

    def entry_generator(self):
        source_collection = utils.get_collection(
            const.CONF_MONGO_ROZPRAVA, self.conf, const.CONF_MONGO_PARSED, self.db
        )
        for entry in source_collection.iterate_all():
            for vystupenie in entry[const.ROZPRAVA_VYSTUPENIA]:
                if const.ROZPRAVA_TLAC in vystupenie:
                    yield {
                        const.NEO4J_BEGINNING_ID: vystupenie[const.MONGO_ID],
                        const.NEO4J_ENDING_ID: vystupenie[const.ROZPRAVA_TLAC]
                    }
