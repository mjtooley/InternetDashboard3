from pymongo import MongoClient
from configuration import getMongoServer, getWindow

class Get:
    """
    This class is used to get the measurements from the database.
    """
    def __init__(self):
        """
        Initialize the class.
        No arguments to MongoClient() connect to the localhost at port 27017.
        Else, arguments to MongoClient() are the IP Address and port number.
        Name of the database is at self.client.DATABASE_NAME
        """
        self.client = MongoClient(getMongoServer(), 27017)
        self.db = self.client.InternetDashboard

    def getMeasurements(self, asn, starttime, endtime):
        """
        Get the measurements according to the ASN, starttime and stoptime. Return the results and the total number of
        results.
        Name of the collection in the database is at self.db.COLLECTION_NAME.find({})
        :param asn:
        :param starttime:
        :param endtime:
        :return all_results, total_number_of_results:
        """
        all_results = self.db.results.find({"asn": asn, "type": "ping", "timestamp": {"$gte": starttime, "$lte": endtime}}, \
                                           no_cursor_timeout=True)
        total_number_of_results = all_results.count()
        return all_results, total_number_of_results

    def getOutages(self, starttime, endtime):
        window = getWindow()
        end = str(endtime - endtime % (60 * window))  # round it to a 15 minute boundary
        dbResults = self.db.outages.find({"date": end})
        if dbResults.count() > 0:
            return True
        else:
            return False

    def getProbe(self,probeId):
        probe = self.db.probes.find_one({"id":probeId})
        return probe


    def closeConnection(self):
        """
        This function closes the connection to the database.
        :return None:
        """
        self.client.close()
        return

    # def getMeasurementsForAverageRTT(self, measurement_id, probe_id, asn, starttime, endtime):
    #     all_results = self.db.results.find({"msm_id": measurement_id, "prb_id": probe_id, "asn": asn, \
    #                                         "timestamp": {"$gt": starttime}, "endtime": {"$lt": endtime}}, \
    #                                        no_cursor_timeout = True)
    #     return all_results
