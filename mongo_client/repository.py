import pymongo

class Repository:

    def __init__(self, connection_string):
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client['facial_embeddings']

    def save_embedding(self, embedding):
        embeddings = self.db['embeddings']
        embeddings.insert_one(embedding)

    def get_all_embeddings(self):
        embeddings = self.db['embeddings']
        return embeddings.find({})