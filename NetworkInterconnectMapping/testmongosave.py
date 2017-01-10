"""
This file is to get the built-in traceroute results originating from ISP ASNs from RIPE Atlas servers and store those
results in MongoDB.
"""

import threading
from pymongo import MongoClient
from ripe.atlas.cousteau import AtlasResultsRequest, ProbeRequest

# Connect to the database using pymongo. No arguments to MongoClient() connects to the localhost at port 27017.
# Else, connect to the database at the specified IP address and port number
client = MongoClient()#"172.25.11.132", 27017)
# Specify the database name at that IP address. (Database Name = Traceroutes)
db = client.TWC1Jan

# Source Network - ASN
# Comcast - 7922
# Cox - 22773
# Charter - 20115
# Cablevision - 6128
# Mediacom - 30036
# TWC - 10796, 11351, 11426, 11427, 12271, 20001
# Suddenlink - 19108
# ATT - 7018, 20057
# Verizon - 701, 702
# Verizon Wireless - 22394
# CenturyLink - 209, 22561
# NCTA - 26868
# Hurricane - 6939
# Cisco - 109, 3943
# Cogent - 174
# Energy Sciences Network - 292
# Internet Systems Consortium - 1280
# NTT Communications - 2914
# Level 3 - 3549
# Frontier Communications - 5650
# TW Telecom - 4323
# Hughes - 6621
# Sonoma Interconnect - 7065
# ViaSat - 7155
# CableOne - 11492
# San Franscisco Metropolitan Internet Exchange - 12276
# Google Fiber - 16591
# Louisiana Optical Network Initiative - 32440
# Bright House Networks - 33363
# Yelp - 33445
# OpenDNS - 36692
# Cloudfare - 394536
# Northland Cable TV - 40285



# Define class myThread to spawn a thread and get results for each ASN from RIPE servers
class myThread(threading.Thread):

    def __init__(self, asn, start_time, stop_time, thread_name):
        threading.Thread.__init__(self)
        self.asn = asn
        self.start_time = start_time
        self.stop_time = stop_time
        self.thread_name = thread_name

    def run(self):
        print "Starting " + self.thread_name
        getASNResults(self.asn, self.start_time, self.stop_time, self.thread_name)
        print "Exiting " + self.thread_name

# Define a function getASNResults() to get built-in traceroute measurements for each ASN in list of source asns
# from RIPE servers
def getASNResults(asn, start_time, stop_time, thread_name):
    # Specify filters to find probes in the US hosted in each ASN in list of source ASNs
    filters = {"asn": asn, "country_code": "US"}
    # Get probes in each ASN using ProbeRequest
    probes = ProbeRequest(**filters)
    # List of measurement ids for built in traceroute measurements
    msm_ids = [5009, 5010, 5011, 5012, 5013, 5004, 5014, 5015, 5005, 5016, 5001, 5008, 5006, 5030, 5031, 5029, 5028, \
               5017, 5019, 5027, 5051, 5151]
    try:
        # Iterate through each probe within an ASN
        for probe in probes:
            # Iterate through each built-in measurement's measurement id
            for msm_id in msm_ids:
                # Specify the filters to find the built-in measurements originating from the probe within a time window
                kwargs = {"msm_id": msm_id, "start": start_time, "stop": stop_time, "probe_ids": probe["id"]}
                # Get results for each built-in measurement and probe using AtlasResultsRequest
                is_success, results = AtlasResultsRequest(**kwargs).create()
                # Continue if successful
                if is_success:
                    # Iterate through all the results
                    for result in results:
                        # print "Sending..."
                        # Add the ASN to the result json to query the database DATABASE NAME
                        result["asn"] = asn
                        print "stop:", result["endtime"]
                        # print result
                        # Add the Target ASN to the result json to query the database DATABASE NAME
                        result["target_asn"] = target_asn
                        # Store the result to the database DATABASE NAME/results
                        # results is the collection name within the database
                        db.results.insert_one(result)
                        # print result["msm_id"], result["prb_id"]
    except:
        pass
    # print "Final stop:", time.time()
    print "Count:", db.results.count()
    print "Fin."

# Start time to get measurements within a time window
start_time = 1451606400
# Stop time to get measurements within a time window
stop_time = 1451606760
# Counter for number of threads
number_of_threads = 0
threads = {}
# Create a list of ASNs from which the measurement originates
# list_of_source_asns = [22773, 20115, 6128, 30036, 10796, 11351, 11426, 11427, 12271, 20001, 19108, 7018, 20057, 701, \
                      # 22394, 209, 22561, 26868, 6939, 109, 3943, 174, 292, 1280, 2914, 3549, 5650, 4323, 6621, 7065, \
                      # 7155, 11492, 12276, 16591, 32440, 33363, 33445, 36692, 394536, 40285, 7922]
list_of_source_asns = [10796]#, 11351, 11426, 11427, 12271, 20001]

# target_asns is used to find results from the database Internet_Dashboard/interconnects, if measurements going to
# Google, Facebook, Amazon, Netflix, Twitter, YouTube from the source ASNs are found.
target_asn = None

# Iterate through all the source ASNs
for asn in list_of_source_asns:
    thread_name = "Thread " + str(asn)
    # Start a thread for each asn
    threads[number_of_threads] = myThread(asn, start_time, stop_time, thread_name)
    threads[number_of_threads].start()
    # Increment counter
    number_of_threads += 1
print "Started " + str(number_of_threads) + " threads."

print "Final fin."