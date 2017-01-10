import json
from datetime import datetime
import time
from GetMeasurements import Get
from FindIPPath import Find
from ResolveMeasurements import Resolve
from CreatingJson import Creating
from pprint import pprint
from ripe.atlas.cousteau import Probe
import geocoder
from geoip import geolite2
import threading
from SaveMeasurements import Save
from configuration import getAsnList,getMongoDB,getmsm_ids
import traceback, sys


class myThread(threading.Thread):
    def __init__(self, start_time, stop_time, source_asns, thread_name):
        threading.Thread.__init__(self)
        self.start_time = start_time
        self.stop_time = stop_time
        self.source_asns = source_asns
        self.thread_name = thread_name

    def run(self):
        #print "Starting " + self.thread_name
        performance(self.start_time, self.stop_time, self.source_asns)
        #print "Exiting " + self.thread_name

def getNetworkName(name_number):
    for hop in name_number:
        if hop["is_boundary"] == True:
            return name_number[name_number.index(hop) - 1]["AS_Name"]

def switchNames(network_dictionary):
    for traceroute in network_dictionary["Networks"]:
        try:
            if "Comcast" in traceroute["Name"]:
                traceroute["Name"] = "Comcast"
            elif ("Verizon" in traceroute["Name"]) or ("UUNET" in traceroute["Name"]) or ("ANS Communications" in traceroute["Name"]):
                traceroute["Name"] = "Verizon"
            elif ("Time Warner Cable" in traceroute["Name"]) or ("ROADRUNNER" in traceroute["Name"]) or ("Charter" in traceroute["Name"]) or ("BRIGHT HOUSE NETWORKS" in traceroute["Name"]):
                traceroute["Name"] = "Charter"
        except Exception as e:
            print "Exception in NetworkPermance SwitchNames",e
    return network_dictionary

def performance(start, end, list_of_source_asns):
    # Format the date and time for the filename
    date_and_time = str(datetime.utcfromtimestamp(start)).replace(" ", "_")

    # To create and store the final json file
    single_result = []

    network_dictionary = {}
    network_dictionary["Networks"] = [{}]
    # network_dictionary["Networks"][-1]["Name"] = "Charter"
    network_dictionary["Networks"][-1]["Aggregate_Routes"] = []

    print "Processing NetworkPerformance:"
    # Iterate through all the source ASNs
    for asn in list_of_source_asns:
        # current_result = 1
        print "--> Perfomance for ASN", asn
        measurements = Get()
        current_measurements = measurements.getMeasurements(asn, start, end)

        counter = 0

        for current_result in current_measurements[0]:
            try:
                # print current_result["result"][-1]["hop"]
                if (current_result["result"][-1]["hop"] != 255) or ("error" in current_result["result"][-1]):
                    counter += 1
                    # pprint(current_result["result"])
                    ip_path = Find(current_result)
                    path = ip_path.findIPPath()
                    #print path[0], len(path[0])
                    #print path[1], len(path[1])
                    #print path[2], len(path[2])
                    as_info = Resolve(path[0], asn)
                    name_number = as_info.resolveMeasurements()
                    # source = as_info.sourceName(current_result["from"])
                    # print source
                    #print name_number
                    single_result.append(name_number)
                    to_json = Creating(network_dictionary, name_number, path[1], path[2])
                    network_dictionary = to_json.creating()

                    network_dictionary["Date"] = "%s" % (date_and_time.replace(":", "-"))
                    network_dictionary["Networks"][-1]["Name"] = getNetworkName(name_number)

            except Exception:
                exc_info = sys.exc_info()
                print "Exception in NetworkPerformance:", exc_info
                traceback.print_exc()

    final_network_dictionary = switchNames(network_dictionary)
    # print "NetworkPerformand Writing..."
    to_save = Save()
    to_save.saveMeasurements(final_network_dictionary)

    measurements.closeConnection()
    to_save.closeConnection()

def computePerformance(asn, result):
    # Format the date and time for the filename
    date_and_time = str(datetime.utcfromtimestamp(time.time())).replace(" ", "_")

    # To create and store the final json file
    single_result = []

    network_dictionary = {}
    network_dictionary["Networks"] = [{}]
    network_dictionary["Networks"][-1]["Aggregate_Routes"] = []

    if (result["result"][-1]["hop"] != 255) or ("error" in result["result"][-1]):
        ip_path = Find(result)
        path = ip_path.findIPPath()

        as_info = Resolve(path[0], asn)
        name_number = as_info.resolveMeasurements()
        single_result.append(name_number)
        to_json = Creating(network_dictionary, name_number, path[1], path[2])
        network_dictionary = to_json.creating()

        network_dictionary["Date"] = "%s" % (date_and_time.replace(":", "-"))
    network_dictionary["Networks"][-1]["Name"] = getNetworkName(name_number)
    final_network_dictionary = switchNames(network_dictionary)
    to_save = Save()
    to_save.saveMeasurements(final_network_dictionary)

def networkPerformance(start, end):
    list_of_source_asns = getAsnList()
    performance(start,end,list_of_source_asns)
    print "-" * 20, "NetworkPeformance Done", "-" * 100


# threaded version
def networkPerformance2(start, end_final):
    # Create a list of ASNs from which that measurement originates
    list_of_source_asns = getAsnList()

    # Start time of the time window and overall interval
    # start = starting_time # 1451606456 # 1475993009, 1475993043

    # End time of the time window. Start time + 6 mins
    end = 0

    # End time of the overall interval
    # end_final = stopping_time # 1451606760 # 1475993020

    # To shift the time window ahead by 6 minutes
    interval = 99

    number_of_threads = 0

    threads = {}

    while end < (end_final - 1):
        # Create a 6 minute interval
        end = start + interval
        thread_name = "Performance " + str(number_of_threads + 1)
        threads[number_of_threads] = myThread(start, end, list_of_source_asns, thread_name)
        threads[number_of_threads].start()
        number_of_threads += 1
        start = end + 1
    print "Started " + str(number_of_threads) + " threads."
