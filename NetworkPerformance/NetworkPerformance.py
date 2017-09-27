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
from configuration import getAsnList,getMongoDB,getmsm_ids, getWindow
import traceback, sys
from ipwhois import IPWhois
from asnlookup import getAsn
from getIpInfo import getLocation
import logging

class PeformanceThread(threading.Thread):
    def __init__(self, start_time, stop_time, source_asns, thread_name):
        threading.Thread.__init__(self)
        self.start_time = start_time
        self.stop_time = stop_time
        self.source_asns = source_asns
        self.thread_name = thread_name

    def run(self):
        #print "Starting " + self.thread_name
        perfomance_d(self.start_time, self.stop_time, self.source_asns)
        # print "Exiting Peformance thread: " + self.source_asns

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

def perfomance_d(start, end, asn):
    logger = logging.getLogger('simpleExample')
    logger.debug('Network peformance for asn: %s',asn)
    Fin=[]
    description = ""
    Net = []
    Route_for_network = {}

    isp_dict = {}  # initialize the dict
    dest_name = ""

    measurements = Get()
    current_measurements = measurements.getMeasurements(asn, start, end)
    d2 = {} # intializie it
    for res in current_measurements[0]:
        RTT_med = 0
        isp_RTT = 0
        list = []
        new_count = 0
        counter = 0
        prev_asn_name = " "
        j=0

        Total_h = len(res['result'])

        try:
            if res['result'][Total_h - 1]['hop'] != 255:
                for i in range(0, Total_h):
                    try:
                        hop_ip = res['result'][i]['result'][0]['from']
                        location= getLocation(hop_ip)

                        new_count += 1
                        now_asn, inter_network_name = getAsn(hop_ip)
                        if j == 0:
                            prev_asn_name = inter_network_name
                            j = 1
                        else:
                            if prev_asn_name != inter_network_name and counter < 1 and now_asn is not None:
                                hop_no = i - 1
                                counter = 1
                                name = prev_asn_name
                                isp_RTT = RTT_med                 # find the edge
                                description = inter_network_name  # ISP Name
                                latitude = location[0]
                                longitude = location[1]
                                #print "-----------------------------------------------EDGE--------------------------------------------------------"

                        #print "Hop ip", i + 1, "    ", hop_ip, "  ", inter_network_name, "  ", now_asn,

                        rtt = []
                        pack_size = res['result'][i]['result'][0]['size']
                        rtt.append(res['result'][i]['result'][0]['rtt'])
                        rtt.append(res['result'][i]['result'][1]['rtt'])
                        rtt.append(res['result'][i]['result'][2]['rtt'])   # find RTT for all three packets
                        RTT_med = sorted(rtt)[len(rtt) // 2]               # find the RTT median
                        dest_name=inter_network_name
                        d1 = {"Name": inter_network_name, "lat": location[0], "lng": location[1], "RTT": RTT_med}
                        list.append(d1)
                        prev_asn = now_asn
                        prev_asn_name = inter_network_name
                        prev_result = location

                    except KeyError: # the traceroute result is **** indicating unknown, so skip.
                        pass

            d2 = {"traceroute": list,
                  "timestamp": res['timestamp'],
                  "Destination": dest_name,
                  "isp": description,
                  "isp_rtt": isp_RTT,
                  "Final_rtt": RTT_med}


            if isp_RTT!=0 and RTT_med!=0:

                if d2['Destination'] in isp_dict:
                    isp_dict[d2['Destination']][0].append((isp_RTT,RTT_med))
                    isp_dict[d2['Destination']].append(d2["traceroute"])
                else:
                    isp_dict[d2['Destination']] = [[(isp_RTT, RTT_med)]]
                    isp_dict[d2['Destination']].append(d2["traceroute"])
        except:
            continue

    dictionary = [ isp_dict]
    try:
        name_net = d2["isp"]  # Get the name of the ISP
    except:
        name_net = "Unknown" \
                   ""
    for k in dictionary:
        a=[]
        Aggregate_Route = []
        lis1 = []
        lis2 = []

        for d in k:
            try:
                if lis1 != [] or lis1 != 0 or lis2 != [] or lis2 != 0:
                    for i in k[d][0]:
                        if i != (0, 0):
                            lis1.append(i[0])
                            lis2.append(i[1])
                    l = filter(lambda a: a != 0, lis1)
                    l2 = filter(lambda a: a != 0, lis2)
                    if l != [] and l2 != [] and l != 0 and l2 != 0:
                        r = reduce(lambda x, y: x + y, l) / len(l)
                        r2 = reduce(lambda x, y: x + y, l2) / len(l2)

                        lat_prb = k[d][1][0]['lat']
                        Lon_prb = k[d][1][0]['lng']
                        name_prb = k[d][1][0]['Name']
                        Len = len(k[d][1])

                        lat_fin = k[d][1][Len - 1]['lat']
                        lon_fin = k[d][1][Len - 1]['lng']
                        name_fin = k[d][1][Len - 1]['Name']
                        k[d] = filter(lambda a: a != 0, k[d])
                        Aggregate_Route = {"Destination": d,
                                           "ISP_RTT": r,
                                           "Traceroutes": k[d],
                                           "Final_RTT": r2,
                                           "Aggregate_Route": [{"Name": name_prb, "lat": lat_prb, "lng": Lon_prb},
                                                               {"Name": name_fin, "lat": lat_fin, "lng": lon_fin}]}
                a.append(Aggregate_Route)
            except Exception:
                exc_info = sys.exc_info()
                traceback.print_exc()
                logger('Exception in NetworkPerformance: %s', exc_info)



        if a!=[]:
            Route_for_network = {"Name": name_net, "Aggregate_Routes": a}
            Net.append(Route_for_network)
        # Fin = filter(None, Net)
        Fin = Net

    if Fin != []:
        # final_network_dictionary = switchNames(network_dictionary)
        prev_name_net = name_net
        Final_1 = {"Networks": Fin}
        global WINDOW
        Final_1["Date"] = str(end - end % (getWindow())) # Put the endtime in as the date, and round it to a 15 minute boundary
        to_save = Save()
        to_save.saveMeasurements(Final_1)
        measurements.closeConnection()
        to_save.closeConnection()


