import constants as const
import storage
import logging
from datetime import datetime
import re

def get_collection(obj, conf, stage, db):
    conf_collections = conf[const.CONF_MONGO][const.CONF_MONGO_DATABASE][
        const.CONF_MONGO_COLLECTION]
    prefix = conf_collections[stage]
    if isinstance(obj, str):
        suffix = obj
    else:
        suffix = str(obj.__class__).split("'")[1].split(".")[-1].lower()
    name = "_".join([prefix, suffix])
    return storage.MongoCollection(db, name)

def camel_case_split(identifier):
    matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return [m.group(0) for m in matches]

def camel2snake(identifier):
    return "_".join([s.lower() for s in camel_case_split(identifier)])

def parse_datetime_csv(date):
    """Format standard datetime string to neo4j format."""
    return "T".join(str(date).split(" "))

def date_converter_csv(s):
    if isinstance(s, datetime):
        return parse_datetime_csv(s)
    else:
        return s 

def parse_klub(s):
    return const.KLUB_DICT.get(s, const.KLUB_NEZARADENI)

def set_up_logging(conf):
    filename = conf.pop(const.CONF_LOGGING_FILENAME)
    logging.basicConfig(
        handlers=[logging.FileHandler(filename, 'w', 'utf-8')], 
        **conf)

def get_poslanec_id(db, name): # priezvisko, meno
    col_names = storage.MongoCollection(db, "nodes_poslanec")
    priezvisko, meno = [s.strip() for s in name.split(",")]
    poslanec = col_names.get(
        {const.POSLANEC_PRIEZVISKO: priezvisko, const.POSLANEC_MENO: meno})
    return poslanec["id"]