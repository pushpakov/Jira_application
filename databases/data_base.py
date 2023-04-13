from pymongo import MongoClient
from dotenv import load_dotenv
import os

# load environment variables from .env file
load_dotenv()

# get environment variables
MONGODB_URI = os.getenv('MONGODB_URI')
DB_NAME = os.getenv('DB_NAME')

USER_COLLECTION = os.getenv('USER_COLLECTION') 
TASK_COLLECTION = os.getenv('TASK_COLLECTION') 
COMMENT_COLLECTION = os.getenv('COMMENT_COLLECTION')  


class MongoConnection:
    def __init__(self, MONGODB_URI,DB_NAME ) :
        self.client = MongoClient(MONGODB_URI) 
        self.db = self.client[DB_NAME] 

    def get_collection(self, COLLECTION_NAME): 
        return self.db[COLLECTION_NAME] 
    



