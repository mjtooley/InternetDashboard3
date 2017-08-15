"""
This file is to get the built-in traceroute and ping results originating from ISP ASNs and store those results in
MongoDB.
"""

import threading
from pymongo import MongoClient
from ripe.atlas.cousteau import AtlasResultsRequest, ProbeRequest, Probe
from socket import socket
from configuration import getAsnList,getMongoServer,getmsm_ids,getCarbonServer,getWindow
import calendar
import time
import datetime
import ConfigParser
import getopt,sys
from NetworkOutage.NetworkOutage import networkOutage, networkOutage2, NetworkOutageThread
from NetworkInterconnectMapping.NetworkInterconnectMapping import networkInterconnects
from NetworkPerformance.NetworkPerformance import PeformanceThread
import geocoder

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
    #print "getASNResults for ",asn
    try:
        client = MongoClient(getMongoServer(), 27017, connect=False)
        # client = MongoClient("172.25.11.23", 27017)
        # Specify the database name at that IP address. (Database Name = InternetDashboard)
        db = client.InternetDashboard
    except:
        print "Couldn't connect to %(server)s , is MongoDB running?" % {'server': getMongoServer()}
        sys.exit(1)

    dbResult = db.results.find({"timestamp": {"$gte": start_time, "$lte": stop_time}}, no_cursor_timeout=True)
    count = dbResult.count()
    if count > 0:
        # Nothing to do as we already have results for this window
        return
    else:
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

            # Store the Probe Information in Database to speed up the other processing
            #print "add probes to DB:", len(probe_list)
            for probe_id in probe_list:
                dbResult = db.probes.find({"id": probe_id})
                if dbResult.count() == 0:
                    probe = Probe(id=probe_id)
                    try:
                        latitude = probe.geometry["coordinates"][1]
                        longitude = probe.geometry["coordinates"][0]
                        location_from_coordinates = geocoder.arcgis([latitude, longitude], method="reverse")
                        state_name = location_from_coordinates.state
                        probe_dict = {"id":probe.id,"ip_address":probe.address_v4,"asn": asn,"longitude":longitude,"latitude":latitude, "state":state_name}
                        try:
                            dbResult = db.probes.insert_one(probe_dict)
                        except Exception as e:
                            pass
                            # print "error adding probe to DB", probe_id, e
                    except:
                        pass # ignore


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
                    #print "ASN:", asn, " TestId:", test_id, " Probes:", len(probe_list), "Count:", len(results)
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
                            except Exception as e :
                                pass

        # print "Finished Updating MongoDB for ASN:", asn," with ",db_writes," records."

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
#sock = socket()
#try:
#  sock.connect( (CARBON_SERVER,CARBON_PORT) )
#except:
#  print "Couldn't connect to %(server)s on port %(port)d, is carbon-agent.py running?" % { 'server':CARBON_SERVER, 'port':CARBON_PORT }
#  sys.exit(1)

def saveToMongoDB(start_time, stop_time):
    #print "Starting SaveToMongoDB"

    # Create the collection and Indexes
    try:
        client = MongoClient(getMongoServer(), 27017, connect=False)
        # client = MongoClient("172.25.11.23", 27017)
        # Specify the database name at that IP address. (Database Name = InternetDashboard)
        db = client.InternetDashboard
    except:
        print "Couldn't connect to %(server)s , is MongoDB running?" % {'server': getMongoServer()}
        sys.exit(1)

    # Add db command to collections to the databases if they don't exist
    db_collections = db.collection_names()
    if 'results' not in db_collections:
        db.create_collection('results', capped=True, size=100000000000)
    if 'probes' not in db_collections:
        db.create_collection('probes', capped=True, size=10000000000)
    if 'outages' not in db_collections:
        db.create_collection('outages', capped=True, size=10000000000)
    if 'interconnects' not in db_collections:
        db.create_collection('interconnects', capped=True, size=10000000000)
    if 'performance' not in db_collections:
        db.create_collection('performance', capped=True, size=10000000000)

    # Check if existing collections are capped
    result = db.command('collstats','results')
    if 'capped' not in result:
        db.command('convertToCapped','results',size=100000000000)

    result = db.command('collstats', 'probes')
    if 'capped' not in result:
        db.command('convertToCapped', 'probes', size=10000000000)

    result = db.command('collstats', 'outages')
    if 'capped' not in result:
        db.command('convertToCapped', 'outages', size=10000000000)

    result = db.command('collstats', 'interconnects')
    if 'capped' not in result:
        db.command('convertToCapped', 'interconnects', size=10000000000)

    result = db.command('collstats', 'performance')
    if 'capped' not in result:
        db.command('convertToCapped', 'performance', size=10000000000)


    # Created indexes and make them unique to ensure there aren't duplicate entries
    try:
        result = db.results.create_index([('prb_id', 1),('msm_id',1),('timestamp',1),('src_addr',1),('dst_addr',1)],unique=True)
        result = db.results.create_index([('timestamp',1)])
    except Exception as e:
        print e
        pass

    # Add a probe index and make them unique
    try:
        result = db.probes.create_index([('id',1)],unique = True)
    except Exception as e:
        print e
        pass

    # For each output collection add an index by "Date' and make it unique
    try:
        result = db.outages.create_index([('Date',1)],unique = True)
    except Exception as e:
        print e
        pass
    try:
        result = db.interconnects.create_index([('Date',1)],unique = True)
    except Exception as e:
        print e
        pass

    try:
        result = db.performance.create_index([('Date',1)],unique = True)
    except Exception as e:
        print e
        pass

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
    print "MongoDB Results DB Updated."
    print "-------------------------------------------\n \n"


def RefreshDatabase(argv):
    configfile = ""
    try:
        opts, args = getopt.getopt(argv, "hc:", ["help", "config="])
    except getopt.GetoptError:
        print("Usage: Internetdashboard.py -c <config file> or Internetdashboard.py --config <config file>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print ('internetdashboard.py [-c <config file>]')
            sys.exit()
        elif opt in ("-c", "--config"):
            configfile = arg

    if configfile != "":
        config = ConfigParser.RawConfigParser(allow_no_value=True)
        config.read(configfile)

        start_string = config.get('Options', 'start')
        date_time_string = start_string
        time_tuple = time.strptime(date_time_string, "%Y-%m-%d %H:%M:%S")
        start_time = calendar.timegm(time_tuple)

        end_string = config.get('Options', 'end')
        date_time_string = end_string
        time_tuple = time.strptime(date_time_string, "%Y-%m-%d %H:%M:%S")
        end_time = calendar.timegm(time_tuple)




    # Update the datebase with the latest results on hourly basis
    start = start_time - start_time % getWindow() # Round it to the hour
    end = start + getWindow() # Hour
    while ( start < end_time):
        print "Refreshing the database with test and computed results."
        print "Start:", datetime.datetime.fromtimestamp(start).strftime(
            '%Y-%m-%d %H:%M:%S'), " End:", datetime.datetime.fromtimestamp(end).strftime('%Y-%m-%d %H:%M:%S')
        saveToMongoDB(start, end)
        list_of_source_asns = getAsnList()
        threads = []
        number_of_threads = 0
        networkOutage(start, end)
        networkInterconnects(start, end)

        for asn in list_of_source_asns:
            thread_name = "Performance " + str(number_of_threads + 1)
            thread = PeformanceThread(start, end, asn, thread_name)
            thread.start()
            threads.append(thread)
            number_of_threads = number_of_threads + 1

        # Wait for all the threads to finish
        for t in threads:
            t.join()
        # move ahead an hour
        start = end
        end = start + getWindow() # Bump it up an hour

    print "Done...."

def main(argv):
    # Jan 1 2017 = 1483228800
    # Jan 10 2017 = 1484006400
    #saveToMongoDB(1483228800, 1484006400)
    RefreshDatabase(argv)


if __name__ == '__main__':
    main(sys.argv[1:])