from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from dotenv import dotenv_values
config = dotenv_values(".env")

URI = config.get('MONGO_URI')


###
# MongoConnection class
# @param: None
# @return: Mongo client
###

class MongoConnection:
    def get_db():
        print('Connecting to MongoDB...')
        client = MongoClient(URI, server_api=ServerApi('1'))

        try:
            client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)

        return client
