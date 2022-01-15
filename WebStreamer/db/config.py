from pymongo import MongoClient
from WebStreamer.vars import Var

def get_database():
    CONNECTION_STRING = "mongodb+srv://teleyer:"+ Var.DB_PASSWORD +"@cluster0.dhmyo.mongodb.net/message_db?retryWrites=true&w=majority"
    client = MongoClient(CONNECTION_STRING)
    db = client['message_db']
    return db
    