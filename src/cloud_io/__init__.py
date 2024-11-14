#Handles cloud related I/O(if needed)

#Here product name will be treated as collection name and reviews as documents
import pandas as pd
from src.exception import CustomException
from src.constants import *
from database_connect import mongo_operation as mongo
import sys,os

class MongoIO:

    mongo_ins=None  #This variable basically helps to establish connection from mongoDB only once,also  a class level variable
    
    def __init__(self):
        if MongoIO.mongo_ins is None:
            mongo_db_url = MONGODB_URL_KEY

            if mongo_db_url is None:
                raise Exception(f"Environment key:{MONGODB_URL_KEY} is not set")
            
            MongoIO.mongo_ins=mongo(client_url=mongo_db_url,database_name=MONGO_DATABASE_NAME)

        self.mongo_ins=MongoIO.mongo_ins

    def store_reviews(self,product_name:str,reviews:pd.DataFrame):
        try:

            collection_name = product_name.replace(' ','_')

            self.mongo_ins.bulk_insert(reviews,collection_name)

        except Exception as e:
            raise CustomException(e,sys) from e

    def get_reviews(self,product_name):
        try:
            collection_name=product_name.replace(' ','_')

            data=self.mongo_ins.find(collection_name) 

            return data
        except Exception as e:
            raise CustomException(e,sys) from e
