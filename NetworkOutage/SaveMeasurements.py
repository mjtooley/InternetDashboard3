from pymongo import MongoClient
from configuration import getMongoServer,getWindow
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
        self.client2 = MongoClient(getMongoServer(), 27017)
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
        # check the number of AS entries, if too few then discard this entry and duplicate the last entry and update the Date
        length = len(result['AS_List'])
        if len(result['AS_List']) < 10:
            try:
                date = int(result['Date']) - getWindow()
                dbLasts = self.db2.outages.find({'Date': date}, no_cursor_timeout=True)
                # dbLast = self.db2.outages.find().sort({'Date':-1}).limit(1);
                count = dbLasts.count()
                if count > 0:
                    for entry in dbLasts:
                        dbLast = entry
                        dbLast['Date'] = result['Date']

                    self.db2.outages.insert_one(dbLast)
                    logger.info('Results too short for %s, so duplicated last result', result['Date'])
            except:
                logger.warning('Exception trying to add a copy of the last outage to the DB')
                pass
        else:
            try:
                self.db2.outages.insert_one(result)
                print "Added Network Outage, Date=", result['Date']
                logger.info('Updated DB with Network Outage %s', result['Date'])

            except Exception as e:
                logger.debug('str(e)')
                pass

    def closeConnection(self):
        """
        This function closes the connection to the database.
        :return None:
        """
        self.client2.close()
        return