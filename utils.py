import constants as const

def get_collection_name(object, conf, stage):
    class_name = str(object.__class__).split("'")[1].split(".")[-1].lower()
    conf_collections = conf[const.CONF_MONGO][const.CONF_MONGO_DATABASE][
        const.CONF_MONGO_COLLECTION]
    suffix = conf_collections[stage]
    prefix = conf_collections[class_name]
    return "_".join([prefix, suffix])