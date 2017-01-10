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

class myThread(threading.Thread):
    def __init__(self, start_time, stop_time, source_asn, thread_name):
        threading.Thread.__init__(self)
        self.start_time = start_time
        self.stop_time = stop_time
        self.source_asn = source_asn
        self.thread_name = thread_name

    def run(self):
        # print "Starting", self.thread_name
        outages(self.start_time, self.stop_time, self.source_asn)
        # print "NetworkOutage Exiting", self.thread_name


def outages(start, end, list_of_source_asns):
    date_and_time = str(datetime.utcfromtimestamp(start)).replace(" ", "_")
    probe_dictionary = {}
    probe_dictionary["Probes"] = []
    probe_dictionary["AS_List"] = []

    print "Processing NetworkOutages:"

    for asn in list_of_source_asns:
        print "-->NetworkOutage:", asn
        current_result = 1
        measurements = Get()
        current_measurement = measurements.getMeasurements(asn, start, end)
        # if current_measurement[1] == 0:
        #     return
        while current_result < current_measurement[1]:
            current_result += 1
            for this_result in current_measurement[0]:
                try:
                    ip_address = this_result["from"]
                    client = IPWhois(ip_address)
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
                final_results["Date"] = "%s" % (date_and_time.replace(":", "-"))

                current_result += 1
                sys.stdout.write('.')

    to_save = Save()
    to_save.saveMeasurements(probe_dictionary)

    measurements.closeConnection()
    to_save.closeConnection()
    print "\n"
    print "-" * 20, "Network Outage Done", "-" * 100

def networkOutage(start, end):
    list_of_source_asns = getAsnList()
    outages(start, end, list_of_source_asns)

# Threaded version
def networkOutage2(start, end_final):

    list_of_source_asns = getAsnList()
    end = 0

    interval = 300

    # date_and_time = str(datetime.utcfromtimestamp(start)).replace(" ", "_")

    packet_dictionary = {}

    number_of_threads = 0

    threads ={}

    while end < (end_final - 1):
        end = start + interval
        thread_name = "NetworkOutage " + str(number_of_threads + 1)
        threads[number_of_threads] = myThread(start, end, list_of_source_asns, thread_name)
        threads[number_of_threads].start()
        number_of_threads += 1
        start = end + 1
    print "NetworkOutage Started %s threads" % str(number_of_threads)

def networkOutageUpdate(measurementResult):
    date_and_time = str(datetime.utcfromtimestamp(time.time())).replace(" ", "_")
    probe_dictionary = {}
    probe_dictionary["Probes"] = []
    probe_dictionary["AS_List"] = []
    # ---
    result_info = Resolve(measurementResult)
    resolved_measurement = result_info.resolveMeasurements()
    if resolved_measurement != None:
        to_json = Creating(probe_dictionary, resolved_measurement)
        final_results = to_json.creatingJson()
        # Add a Date key
        final_results["Date"] = "%s" % (date_and_time.replace(":", "-"))
    # ---
    to_json.checkNetworkName(probe_dictionary)
    to_save = Save()
    to_save.saveMeasurements(probe_dictionary)
    to_save.closeConnection()

