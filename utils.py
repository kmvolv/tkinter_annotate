from pymongo import MongoClient
import pickle
import json

def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance


@singleton
class MongoHelper:
    MONGO_COLLECTION_PARTS = "parts"
    MONGO_COLLECTIONS = {MONGO_COLLECTION_PARTS: "parts"}
    client = None
    def __init__(self):
        if not self.client:
            self.client = MongoClient(host="host.docker.internal", port=27017)
        self.db = self.client["SEPCBA"]

    def getDatabase(self):
        return self.db

    def getCollection(self, cname, create=False, codec_options=None):
        _DB = "SEPCBA"
        DB = self.client[_DB]
        if cname in self.MONGO_COLLECTIONS:
            if codec_options:
                return DB.get_collection(self.MONGO_COLLECTIONS[cname], codec_options=codec_options)
            return DB[self.MONGO_COLLECTIONS[cname]]
        else:
            return DB[cname]


