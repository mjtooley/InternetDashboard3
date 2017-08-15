__author__ = 'mtooley'
# import requests
import json
# import urllib2
# from datetime import datetime
import time
import sys
import ujson
from ripe.atlas.cousteau import  AtlasStream,MeasurementRequest, AtlasResultsRequest, ProbeRequest, AtlasLatestRequest
from ripe.atlas.cousteau import Probe, Measurement
from socket import socket
from ripe.atlas.sagan import SslResult
from ripe.atlas.sagan import PingResult,TracerouteResult, DnsResult, HttpResult
import threading
from configuration import getAsnList,getMongoServer,getmsm_ids,getCarbonServer
from pymongo import MongoClient

from NetworkInterconnectMapping.NetworkInterconnectMapping import networkInterconnects,computeNetworkInterconnects

from SaveToMongoDB import saveToMongoDB,saveResultToMongDB


class myThread(threading.Thread):
    def __init__(self, asn, msm, probeid):
        threading.Thread.__init__(self)
        self.asn = asn
        self.msm = msm
        self.probeid = probeid
    def run(self):
        print "Starting "  + "ProbeID:" + str(self.probeid)+ " ASN:" + str(self.asn) + " msm_id:" + str(self.msm)
        start_thread_stream(self.asn, self.msm, self.probeid)




def start_thread_stream( asn, msm, probeid):
    kwargs = {
            "msm": msm,
            "prb": probeid
    }
#    print "Subscribe for ", asn, test_id, probe["id"]
    try:
        atlas_stream.start_stream(stream_type="result", **kwargs)
    except:
        print "error subscribing to stream"


############################################
#  on_result
#  This is called each time a new result for the measurement is received
#
##############################################

def on_result_response(*args):
    print args[0]
    result = (args[0])
    result_type = result["msm_name"]
    probeid = result["prb_id"]
    probe = Probe(id=probeid)
    asn = probe.asn_v4

    ##################################
    # Put Metric Computation Code here
    ##################################
    #    networkOutageUpdate(result)
    #    computeNetworkInterconnects(asn,result)
    #    computePerformance(asn,result)

    if saveResultToMongDB(asn,result):
        # Save Time-series Metrics to Carbon/Whisper
        message = "dashboard.mongodb.write"  + "." + "success " + "1" + " " + str(result["timestamp"]) + "\n"
    else:
        message = "dashboard.mongodb.write"  + "." + "fail " + "1" + " " + str(result["timestamp"]) + "\n"

    # print message
    sock.sendall(message) # send the result to Carbon/Graphite
# ##########################################

############################################
#
#  Code below is framework to launch a thread per streaming
#  measurement
#
######################################################

atlas_stream = AtlasStream()  # Create a stream for Atlas results
atlas_stream.connect()  # Connect to the atlast server
channel = "result"  # Define the stream to get "results".  Other choices are 'probe' connection status

# Bind function we want to run with every result message received
atlas_stream.bind_channel(channel, on_result_response)

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

MONGODB_HOST = getMongoServer()
MONGODB_PORT = 27017
# MongoDB
client = MongoClient(MONGODB_HOST,MONGODB_PORT)
db = client.InternetDashboard # Switch to the  database in Mongo

def getStreamResults():

    print "starting getStreamResults"

    L_asns = getAsnList()
    msm_ids = getmsm_ids()
    thread = {} # create a dictionary to hold the threads
    i =0
    for asn in L_asns:
        filters = {"asn": asn }
        probe_list = []
        probes = []
        try:
            probes = ProbeRequest(**filters) # Get all the probes on the ASN
        except:
            print "error getting probes", probes

        try:
            for probe in probes:
                for test_id in msm_ids:
                    kwargs = {
                        "msm": test_id,
                        "prb": probe["id"]
                    }
                    # Streams are blocking, so create a thread for each streamed result.
                    thread[i] = myThread(asn, test_id, probe["id"])
                    thread[i].start() # start the stream

                    i = i + 1 # increment the thread id
        except Exception as e:
            print e

    # print "Started " + str(i) + " threads"
    atlas_stream.timeout() # Stay connected for infinity

    print("Finished running getStreamResults")




def main():
    getStreamResults()

if __name__ == '__main__':
    main()