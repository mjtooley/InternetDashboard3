from pymongo import MongoClient
from configuration import getAsnList,getMongoServer,getmsm_ids
import datetime
import logging

class Save:
    """
    This class is used to save the json files back to the database.
    """
    def __init__(self):
        """
        Initialize the class.
        No arguments to MongoClient() connect to the localhost at port 27017.
        Else, arguments to MongoClient() are the IP Address and port number.
        Name of the database is at self.client2.DATABASE_NAME
        """
        mongoServer = getMongoServer()
        self.client2 = MongoClient(mongoServer, 27017)
        self.db2 = self.client2.InternetDashboard

    def saveMeasurements(self, result):
        """
        This function saves the result to the database.
        Name of the collection in the database is at self.db2.COLLECTION_NAME.insert_one(result)
        :param result:
        :return:
        """
        logger = logging.getLogger('simpleExample')
        result['createdAt'] = datetime.datetime.now()  # Get the time now in UTC format
        try:
            self.db2.interconnects.insert_one(result)
            logger.info('-->Interconnect DB Write Result, Date= %s',result['Date'])
        except:
            pass


    def closeConnection(self):
        """
        This function closes the connection to the database.
        :return None:
        """
        self.client2.close()
        return