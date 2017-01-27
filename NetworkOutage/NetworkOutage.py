import json
import threading
import sys
import fcntl
from datetime import datetime
import time
from ResolveMeasurements import Resolve
from GetMeasurements import Get
from CreatingJson import Creating
from MergingJson import Merging
from ipwhois import IPWhois
from SaveMeasurements import Save
# from cymruwhois import Client
from IPy import IP
from ripe.atlas.sagan import PingResult
from ripe.atlas.cousteau import Probe
import geocoder
from configuration import getAsnList,getMongoDB,getmsm_ids

class NetworkOutageThread(threading.Thread):
    def __init__(self, start_time, stop_time, source_asn, thread_name):
        threading.Thread.__init__(self)
        self.start_time = start_time
        self.stop_time = stop_time
        self.source_asn = source_asn
        self.thread_name = thread_name

    def run(self):
        # print "Starting", self.thread_name
        outagesThread(self.start_time, self.stop_time, self.source_asn)
        print "NetworkOutage Exiting:", self.source_asn

# Threaded version
def outagesThread(start, end, asn):
    date_and_time = str(datetime.utcfromtimestamp(start)).replace(" ", "_")
    probe_dictionary = {}
    probe_dictionary["Probes"] = []
    probe_dictionary["AS_List"] = []


    current_result = 1
    measurements = Get()
    current_measurement, number_of_results = measurements.getMeasurements(asn, start, end)

    print "-->NetworkOutage:", asn, " total measurements:", number_of_results

    for this_result in current_measurement:
        try:
            ip_address = this_result["from"]
            # client = IPWhois(ip_address)
        except Exception as e:
            print e
            current_result += 1
            continue
        result_info = Resolve(this_result)
        resolved_measurement = result_info.resolveMeasurements()
        if resolved_measurement == None:
            continue
        to_json = Creating(probe_dictionary, resolved_measurement)
        to_json.checkNetworkName(probe_dictionary)

        final_results = to_json.creatingJson()
        #final_results["Date"] = "%s" % (date_and_time.replace(":", "-"))
        final_results["Date"] = str(end - end % (60*15)) # Put the endtime in as the date, and round it to a 15 minute boundary

        current_result += 1
        # sys.stdout.write('.')
        # print "Measurement:", current_result
        #

    to_save = Save()
    to_save.saveMeasurements(probe_dictionary)

    measurements.closeConnection()
    to_save.closeConnection()
    print "Finished NetworkOutage:", asn

def networkOutage2(start, end):

    list_of_source_asns = getAsnList()
    threads =[]
    number_of_threads = 0

    for asn in list_of_source_asns:
        thread_name = "NetworkOutage " + str(number_of_threads + 1)
        thread = NetworkOutageThread(start, end, asn, thread_name)
        thread.start()
        threads.append(thread)
        number_of_threads = number_of_threads + 1
        start = end + 1

    # Wait for all the threads to finish
    for t in threads:
        t.join()
    print "All threads finished, Exiting NetworkOutage2"

##########################################################

def outages(start, end, list_of_source_asns):
    date_and_time = str(datetime.utcfromtimestamp(start)).replace(" ", "_")
    probe_dictionary = {}
    probe_dictionary["Probes"] = []
    probe_dictionary["AS_List"] = []
    probe_list = {}

    print "Processing NetworkOutages:"

    for asn in list_of_source_asns:
        print "-->NetworkOutage:", asn
        current_result = 1
        measurements = Get()
        current_measurement = measurements.getMeasurements(asn, start, end)

        for this_result in current_measurement[0]:
            try:
                ip_address = this_result["from"]
                client = IPWhois(ip_address)
            except Exception as e:
                print e
                current_result += 1
                continue
            result_info = Resolve(this_result,probe_list)
            resolved_measurement = result_info.resolveMeasurements()
            if resolved_measurement == None:
                continue
            probe = resolved_measurement[3]
            id = probe['id']
            if id not in probe_list:
                probe_list[id] = probe # Add the probe to the cache

            to_json = Creating(probe_dictionary, resolved_measurement)
            to_json.checkNetworkName(probe_dictionary)

            final_results = to_json.creatingJson()
            final_results["Date"] = str(end - end % (60*15)) # Put the endtime in as the date, and round it to a 15 minute boundary

            current_result += 1
            # sys.stdout.write('.')

    to_save = Save()
    to_save.saveMeasurements(probe_dictionary)

    measurements.closeConnection()
    to_save.closeConnection()
    print "\n"
    print "-" * 20, "Network Outage Done", "-" * 100

def networkOutage(start, end):
    list_of_source_asns = getAsnList()
    outages(start, end, list_of_source_asns)