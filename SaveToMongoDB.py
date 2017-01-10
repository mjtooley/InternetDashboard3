"""
This file is to get the built-in traceroute and ping results originating from ISP ASNs and store those results in
MongoDB.
"""

import threading
from pymongo import MongoClient
from ripe.atlas.cousteau import AtlasResultsRequest, ProbeRequest
from configuration import getAsnList,getMongoServer,getmsm_ids
import sys
from socket import socket
from configuration import getAsnList,getMongoServer,getmsm_ids,getCarbonServer
import datetime



# Define class myThread to spawn a thread and get results for each ASN from RIPE servers
class myThread(threading.Thread):

    def __init__(self, asn, start_time, stop_time, thread_name, target_asn):
        threading.Thread.__init__(self)
        self.asn = asn
        self.start_time = start_time
        self.stop_time = stop_time
        self.thread_name = thread_name
        self.target_asn = target_asn

    def run(self):
        #print "Starting " + self.thread_name
        getASNResults(self.asn, self.start_time, self.stop_time, self.target_asn)
        #print "Exiting " + self.thread_name

# Define a function getASNResults() to get built-in traceroute measurements for each ASN in list of source asns
# from RIPE servers
def getASNResults(asn, start_time, stop_time, target_asn):

    db_writes = 0 # intialize db write counter
    print "getASNResults for ",asn
    try:
        client = MongoClient(getMongoServer(), 27017, connect=False)
        # client = MongoClient("172.25.11.23", 27017)
        # Specify the database name at that IP address. (Database Name = InternetDashboard)
        db = client.InternetDashboard
    except:
        print "Couldn't connect to %(server)s , is MongoDB running?" % {'server': getMongoServer()}
        sys.exit(1)

    msm_ids = getmsm_ids()

    ## print("Getting Probes for ASN", asn)
    for test_id in msm_ids:
        filters = {"id": test_id, "asn": asn}
        probe_list = []
        probes = []
        try:
            probes = ProbeRequest(**filters)
        except:
            print "error getting probes", probes

        try:
            if probes:
                for probe in probes:
                    probe_list.append(probe["id"])  # add the probe ID to the list
        except:
            e = sys.exc_info()
            print ("Probe error", str(e))
            probe_list = []

        # Get the all the measurments of interest for these probes

        if len(probe_list) > 0:
            kwargs = {
                "msm_id": test_id,
                "start": start_time,
                "stop": stop_time,
                "probe_ids": probe_list
            }

            is_success, results = AtlasResultsRequest(**kwargs).create()

            if is_success:
                print "ASN:", asn, " TestId:", test_id, " Probes:", len(probe_list), "Count:", len(results)
                for res in results:
                    if res != 'error':
                        try:
                            res['asn'] = asn
                            res['createdAt'] = datetime.datetime.now() # Get the time now in UTC format
                            dbResult = db.results.insert_one(res)
                            if dbResult:
                                # Save Time-series Metrics to Carbon/Whisper
                                message = "dashboard.mongodb.write" + "." + "success " + "1" + " " + str(
                                    res["timestamp"]) + "\n"
                                #print message
                                sock.sendall(message)  # send the result to Carbon/Graphite
                                db_writes = db_writes + 1
                            else:
                                message = "dashboard.mongodb.write" + "." + "fail " + "1" + " " + str(
                                    res["timestamp"]) + "\n"
                                #print message
                                sock.sendall(message)  # send the result to Carbon/Graphite
                        except:
                            e = sys.exc_info()
                            print("Error Writing  to DB: ", str(e))

    print "Finished Updating MongoDB for ASN:", asn," with ",db_writes," records."

def saveResultToMongDB(asn, result):
    try:
        client = MongoClient(getMongoServer(), 27017, connect=False)
        # client = MongoClient("172.25.11.23", 27017)
        # Specify the database name at that IP address. (Database Name = InternetDashboard)
        db = client.InternetDashboard
    except:
        print "Couldn't connect to %(server)s , is MongoDB running?" % {'server': getMongoServer()}
        sys.exit(1)

    result["asn"] = asn
    # result["target_asn"] = target_asn
    try:
        dbResult = db.results.insert_one(result)
        return True
    except Exception as e:
        print e
        return False

# Local Carbon/Graphite Server Settings
CARBON_SERVER = getCarbonServer()
CARBON_PORT = 2003

#Open Graphite/Carbon connection
sock = socket()
try:
  sock.connect( (CARBON_SERVER,CARBON_PORT) )
except:
  print "Couldn't connect to %(server)s on port %(port)d, is carbon-agent.py running?" % { 'server':CARBON_SERVER, 'port':CARBON_PORT }
  sys.exit(1)

def saveToMongoDB(start_time, stop_time):
    print "Starting SaveToMongoDB"

    # Counter for number of threads
    number_of_threads = 0
    threads = []
    # Create a list of ASNs from which the measurement originates

    list_of_source_asns = getAsnList()
    # target_asns is used to find results from the database Internet_Dashboard/interconnects, if measurements going to
    # Google, Facebook, Amazon, Netflix, Twitter, YouTube from the source ASNs are found.
    target_asn = None

    # Iterate through all the source ASNs
    for asn in list_of_source_asns:
        thread_name = "MongoDB " + str(asn)
        # Start a thread for each asn
        thread = myThread(asn, start_time, stop_time, thread_name, target_asn)
        thread.start()
        threads.append(thread)
        # getASNResults(asn,start_time,stop_time, target_asn) # Single Threaded version
        # Increment counter
        number_of_threads += 1

    # Wait for all threads to finish
    for t in threads:
        t.join()
    print "All threads finished, exiting saveToMongoDB."
    print "-------------------------------------------\n \n"

def main():
    saveToMongoDB(1451606400, 1451606760)

if __name__ == '__main__':
    main()