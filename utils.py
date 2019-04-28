# Load external modules.
from datetime import datetime
import logging
import re

# Load internal modules.
import constants as const
import storage

class Logged:
    def __init__(self):
        self.log = logging.getLogger(str(self.__class__).split("'")[1])

def camel_case_split(identifier):
    matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return [m.group(0) for m in matches]

def camel_to_snake(identifier):
    return '_'.join([s.lower() for s in camel_case_split(identifier)])

def parse_datetime_csv(date):
    """Format standard datetime string to neo4j format."""
    return 'T'.join(str(date).split(' '))

def date_converter_csv(s):
    if isinstance(s, datetime):
        return parse_datetime_csv(s)
    else:
        return s

def parse_klub(s):
    return const.KLUB_DICT.get(s, const.KLUB_NEZARADENI)

def get_poslanec_id(db, name): # priezvisko, meno
    col_names = storage.MongoCollection(db, 'nodes_poslanec')
    priezvisko, meno = [s.strip() for s in name.split(',')]
    poslanec = col_names.get({
        const.POSLANEC_PRIEZVISKO: priezvisko,
        const.POSLANEC_MENO: meno
    })
    return poslanec['id']
