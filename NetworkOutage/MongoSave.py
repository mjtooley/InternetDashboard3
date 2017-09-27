"""
This file is to get the built-in ping results originating in the ISP ASNs from RIPE Atlas servers and store those
results in MongoDB.
"""

import threading
from pymongo import MongoClient
from ripe.atlas.cousteau import AtlasResultsRequest, ProbeRequest, MeasurementRequest
import logging

# Connect to the database using pymongo. No arguments to MongoClient() connects to the localhost at port 27017.
# Else, connect to the database at the specified IP address and port number
client = MongoClient("172.25.11.109", 27017)
# Specify the database name at that IP address. (Database Name = Pings)
db = client.InternetDashboard

# Define class myThread to spawn a thread and get results for each ASN form RIPE servers
class myThread(threading.Thread):

    def __init__(self, asn, start_time, stop_time, thread_name):
        threading.Thread.__init__(self)
        self.asn = asn
        self.start_time = start_time
        self.stop_time = stop_time
        self.thread_name = thread_name

    def run(self):
        print "Starting " + self.thread_name
        getPingResults(asn, start_time, stop_time)
        print "Exiting " + self.thread_name

# Define a function getPingResults to get built-in ping measurements for each ASN in list of source ASNs from RIPE
# servers
def getPingResults(asn, start_time, stop_time):
    # Specify filters to find probes in the US hosted in each ASN in list of source ASNs
    filters = {"asn": asn, "country_code": "US"}
    # Get probes in each ASN using ProbeRequest
    probes = ProbeRequest(**filters)
    # List of measurement ids for built in ping measurements
    msm_ids = [1009, 1010, 1011, 1012, 1013, 1004, 1014, 1015, 1005, 1016, 1001, 1008, 1006, 1030, 1031, 1029, 1028,
               1017, 1019, 1027, 2009, 2010, 2011, 2012, 2013, 2004, 2014, 2015, 2005, 2016, 2001, 2008, 2006, 2030,
               2031, 2029, 2028, 2017, 2019, 2027]
    # mfilters = {"type": "ping", "asn": asn}
    # msm_ids = MeasurementRequest(**mfilters)

    # Iterate through each probe within an ASN
    for probe in probes:
        # Iterate through each measurement's measurement id
        for msm_id in msm_ids:
            # Specify the filters to find the measurements originating from the probe within a time window
            kwargs = {"msm_id": msm_id, "start": start_time, "stop": stop_time, "probe_ids": probe["id"]}
            # Get results for each measurement and probe using AtlasResultsRequest
            is_success, results = AtlasResultsRequest(**kwargs).create()
            # Continue if successful
            if is_success:
                # Iterate through all the results
                for result in results:
                    # Add the ASN to the result json to query the database DATABASE NAME
                    result["asn"] = asn
                    print "time: %s, asn: %s" % (result["timestamp"], asn)
                    # Add the Target asn to the result json to query the database DATABASE NAME
                    result["target_asn"] = target_asn
                    # Store the result to the database DATABASE NAME/results
                    # results is the collection name within the database
                    db.pings.insert_one(result)

    print "Count:", db.pings.count()
    print "Fin."
print "Finally fin."


# Start time to get measurements within a time window
start_time = 1409126400
# Stop time to get mesurements within a time window
stop_time = 1409126700
# Counter for number of threads
number_of_threads = 0
threads = {}

# Create a list of ASNs from which the measurement originates
list_of_source_asns = [10796, 11351, 11426, 11427, 12271, 20001]

# target_asns is used to find results from the database Internet_Dashboard/outages, if measurements going to Google,
# Facebook, Amazon, Netflix, Twitter, YouTube from the source ASNs are found.
target_asn = None

# Iterate through all the source ASNs
for asn in list_of_source_asns:
    thread_name = "Thread " + str(asn)
    # Start a thread for each asn
    threads[number_of_threads] = myThread(asn, start_time, stop_time, thread_name)
    threads[number_of_threads].start()
    # Increment counter
    number_of_threads += 1

print "Started " + str(number_of_threads) + " threads"


# import json
# from pymongo import MongoClient
# from ripe.atlas.sagan import TracerouteResult, Result
# from ripe.atlas.cousteau import AtlasResultsRequest, AtlasLatestRequest, ProbeRequest, MeasurementRequest
#
# client = MongoClient()
# db = client.TWCPings
#
# list_of_source_asns = [10796, 11351, 11426, 11427, 12271, 20001]#[2856, 5400, 12641]#7843, 10796, 11351, 11426, 11427, 12271, 20001, 11955, 7922, 3447,2379,4282, 10825, 3561, 3908, 3909, 26868,  702, 703, 704, 705, 284, 6066, 13433, 3356, 19108, 3420, 3421, 7843, 10796, 11351, 11426, 11427, 12271, 20001, 11955, 209,701]#
# target_asn = None
# i = 0
# for asn in list_of_source_asns:
#  start_time = 1475478000
#  stop_time = 1475503200
#
#  filters = {"asn": asn}
#  probes = ProbeRequest(**filters)
#  mfilters = {"type": "ping", "asn": asn}
#  msm_ids = MeasurementRequest(**mfilters)#[1009, 1010, 1011, 1012, 1013, 1004, 1014, 1015, 1005, 1016, 1001, 1008, 1006]
#
#  for probe in probes:
#      for msm_id in msm_ids:
#          print 'requesting...'
#          print msm_id
#          i = i + 1
#          kwargs = {"msm_id": msm_id["id"], "start": start_time, "stop": stop_time, "probe_ids": probe["id"]}
#          is_success, results = AtlasResultsRequest(**kwargs).create()
#
#          if is_success:
#              for res in results:
#                  print "Sending..."
#                  res["asn"] = asn
#                  res["target_asn"] = target_asn
#                  db.results.insert_one(res)
#                  print res["msm_id"], res["prb_id"]
#          else:
#              print 'Failed'
# #print "Count:", db.results.count()
#                  # dbresult = db.results.insert_one(dict(TracerouteResult(res)))
#                  # print dbresult.inserted_id
# print "Fin."