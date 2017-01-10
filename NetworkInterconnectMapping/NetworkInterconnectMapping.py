import json
import threading
from FindIPPath import Find
from datetime import datetime
from GetMeasurements import Get
from CreatingJson import Creating
from SaveMeasurements import Save
from FindMedianRTT import FindMedianRTT
from ResolveMeasurements import Resolve
from configuration import getAsnList,getMongoDB,getmsm_ids
import time
import traceback
import sys


# Start time to calculate the Average RTT for a time interval before the start time
# start_historic = 1470103200
# End time to calculate the Average RTT for a time interval before the end time
# end_historic = 0
# To shift the historic time window ahead with respect to the current measurement time window to calculate the
# Average RTT
# interval_historic = 7199

class myThread(threading.Thread):

    def __init__(self, start_time, stop_time, source_asns, thread_name):
        threading.Thread.__init__(self)
        self.start_time = start_time
        self.stop_time = stop_time
        self.source_asns = source_asns
        self.thread_name = thread_name

    def run(self):
        # print "Starting " + self.thread_name
        interconnects(self.start_time, self.stop_time, self.source_asns)
        # print "Exiting " + self.thread_name

# While loop to find measurements for the whole time window
def interconnects(start, end, list_of_source_asns):
    # Format the date and time for the filename
    date_and_time = str(datetime.utcfromtimestamp(start)).replace(" ", "_")
    # To create and store the final json file
    neighbor_dictionary = {}
    # neighbor_dictionary["AS_List"] = []
    neighbor_dictionary["Nodes"] = []
    neighbor_dictionary["Links"] = []
    neighbor_dictionary["Backbone_AS_List"] = []
    neighbor_dictionary["Source_List"] = []
    # To save the json file locally instead of the database
    # file_save = open("/home/pranav/PycharmProjects/RIPE_Atlas_v4/VisualizationsLocal/Interconnect/TestData/%s.json" % \
    # date_and_time.replace(":", "-"), "w+")
    # file_save.read()

    print "Processing Interconnects...."
    # Iterate through all the source ASNs
    for asn in list_of_source_asns:
        # Counter to stop at the total number of measurements available within a time window for an ASN
        current_result = 1
        # Initialize an object from the class Get() defined in GetMeasurements.py and assign it to measurements
        measurements = Get()
        # Get all the measurements from the database DATABASE_NAME/results according to ASN and a time window
        current_measurement = measurements.getMeasurements(asn, start, end)
        # print current_measurement[0]
        # Initialize an object from the class Creating() defined in CreatingJson.py and assign it to to_json
        to_json = Creating(neighbor_dictionary, asn, False, True)

        print "--> Interconnects for ASN:",asn
        # While loop to break after iterating through all the measurements in a time window
        while current_result < current_measurement[1]:
            try:
                # Iterate through all the measurements in a time window
                for this_result in current_measurement[0]:
                    # measurement_index = current_measurement[0].cursor_id
                    #print "Measurement ID: %s, Probe ID: %s, Current: %s" % \
                    #      (this_result["msm_id"], this_result["prb_id"], current_result)
                    # Initialize an object from the class Find() defined in FindIPPath.py and assign it to ip_path
                    ip_path = Find(this_result)
                    # Find the IP Path of the current traceroute measurement
                    path = ip_path.findIPPath()
                    # Initialize an object from the class FindMedianRTT() defined in FindMedianRTT.py and assign it
                    # to rtt
                    rtt = FindMedianRTT(this_result)
                    # Find the median RTT for each hop of the current traceroute measurement
                    median_rtts = rtt.findMedianRTT()

                    # Initialize an object from the class FindAverageRTT() defined in FindAverageRTT.py and assign it
                    #  to get_average
                    # get_average = FindAverageRTT(this_result["msm_id"], this_result["prb_id"], asn, start_historic, \
                    # end_historic)
                    # Find the average RTT of the same measurement from the historic data for a time window before
                    # the current start time
                    # average_median_rtts = get_average.findAverage()

                    # Initialize an object from the class Resolve() defined in ResolveMeasurements.py and assign it
                    # to as_info
                    as_info = Resolve(path, asn, None)#, this_result["target_asn"])
                    # Find the network boundary/boundaries and get the AS Name, ASN and Hopnumber of each boundary
                    try:
                        name_number = as_info.resolveMeasurements()
                    except:
                        exc_info = sys.exc_info()
                        print "Exception in NetworkInterconnect1:", exc_info
                        traceback.print_exc()
                        name_number = {} # Empty List

                    # Create a json file and assign it to final_results
                    final_results = to_json.creatingJson(name_number, median_rtts)
                    # Add a Date key to find the json file from the database Internet_Dashboard/interconnects to
                    # display using d3
                    final_results["Date"] = "%s" % (date_and_time.replace(":", "-"))
                    # print "result:", current_result, " final_results ", final_results
                    # Increment the counter
                    current_result += 1
            except Exception:
                exc_info = sys.exc_info()
                print "Exception in NetworkInterconnect", exc_info
                traceback.print_exc()
                # name_number = as_info.resolveMeasurements()
                # print name_number
                # # Create a json file and assign it to final_results
                # final_results = to_json.creatingJson(name_number, median_rtts)
                # # Add a Date key to find the json file from the database Internet_Dashboard/interconnects to
                # # display using d3
                # final_results["Date"] = "%s" % (date_and_time.replace(":", "-"))
                # Increment the counter
                current_result += 1
                continue


    if 'final_results' in locals():
        # Move the time window ahead by 30 minutes
        # start = end + 1
        # Move the time window to calculate the Average RTT ahead by interval
        # start_historic = start_historic + interval + 1
        print "Writing..."
        # print json.dumps(final_results, sort_keys=True, indent=4, separators=(",", ": "))
        # Initialize an object from the class Save() defined in SaveMeasurements.py and assign it to to_save
        to_save = Save()
        # Save the json file in final_results to the database Internet_Dashboard/interconnects
        to_save.saveMeasurements(final_results)
        to_save.closeConnection()
        # Write the json file in final_results to the local file

    # print "Closing..."
    measurements.closeConnection()

def networkInterconnects(start, end):
    list_of_source_asns = getAsnList()
    interconnects(start,end,list_of_source_asns)
    print "-" * 20, "NetworkInterconnect Done", "-" * 100

def networkInterconnects2(start, end_final):
    # Create a list of ASNs from which the measurement originates

    list_of_source_asns = getAsnList()
    # target_asns is used to find results from the database Internet_Dashboard/interconnects, if measurements going to
    # Google, Facebook, Amazon, Netflix, Twitter, YouTube from the source ASNs are found.
    target_asns = None
    # Start time of the time window and overall interval
    # start = 1475992800
    # End time of the time window. Start time + 30 minutes
    end = 0
    # End time of the overall interval
    # end_final = 1476003600
    # To shift the time window ahead by 30 minutes
    interval = 1799
    number_of_threads = 0
    threads = {}

    while end < (end_final - 1):
        # Create a 30 minute time interval
        end = start + interval
        thread_name = "Interconnect " + str(number_of_threads + 1)
        # Start a thread for each time interval
        threads[number_of_threads] = myThread(start, end, list_of_source_asns, thread_name)
        threads[number_of_threads].start()
        # Increment counter
        number_of_threads += 1
        start = end + 1
    print "Started " + str(number_of_threads) + " threads."

def computeNetworkInterconnects(asn, result):

    # Format the date and time for the filename
    date_and_time = str(datetime.utcfromtimestamp(time.time())).replace(" ", "_")

    # To create and store the final json file
    neighbor_dictionary = {}

    neighbor_dictionary["Nodes"] = []
    neighbor_dictionary["Links"] = []
    neighbor_dictionary["Backbone_AS_List"] = []
    neighbor_dictionary["Source_List"] = []

    # Initialize an object from the class Creating() defined in CreatingJson.py and assign it to to_json
    to_json = Creating(neighbor_dictionary, asn, False, True)

    # Initialize an object from the class Find() defined in FindIPPath.py and assign it to ip_path
    ip_path = Find(result)

    # Find the IP Path of the current traceroute measurement
    path = ip_path.findIPPath()

    # Initialize an object from the class FindMedianRTT() defined in FindMedianRTT.py and assign it
    # to rtt
    rtt = FindMedianRTT(result)

    # Find the median RTT for each hop of the current traceroute measurement
    median_rtts = rtt.findMedianRTT()

    # Initialize an object from the class FindAverageRTT() defined in FindAverageRTT.py and assign it
    #  to get_average
    # get_average = FindAverageRTT(this_result["msm_id"], this_result["prb_id"], asn, start_historic, \
    # end_historic)
    # Find the average RTT of the same measurement from the historic data for a time window before
    # the current start time
    # average_median_rtts = get_average.findAverage()

    # Initialize an object from the class Resolve() defined in ResolveMeasurements.py and assign it
    # to as_info
    as_info = Resolve(path, asn, None)  # , this_result["target_asn"])

    # Find the network boundary/boundaries and get the AS Name, ASN and Hopnumber of each boundary
    name_number = as_info.resolveMeasurements()


    # Create a json file and assign it to final_results
    final_results = to_json.creatingJson(name_number, median_rtts)
    # Add a Date key to find the json file from the database Internet_Dashboard/interconnects to
    # display using d3
    final_results["Date"] = "%s" % (date_and_time.replace(":", "-"))

    to_save = Save()
    # Save the json file in final_results to the database Internet_Dashboard/interconnects
    to_save.saveMeasurements(final_results)

