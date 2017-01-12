import traceback
import sys
from collections import defaultdict

class Creating(object):
    def __init__(self, network_dictionary, name_number, location, rtt):
        self.network_dictionary = network_dictionary
        self.location = location
        self.rtt = rtt
        self.name_number = name_number

    def traceroutePresent(self, destination):
        aggregate_routes_index = -1
        for aggregate_routes_index in range(0, len(self.network_dictionary["Networks"][-1]["Aggregate_Routes"])):
            if self.name_number[destination]["AS_Name"] == self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Destination"]:
                break
            else:
                aggregate_routes_index = -1

        return aggregate_routes_index

    def addAggregateRoutes(self, aggregate_routes_index, destination, boundary):
        self.network_dictionary["Networks"][-1]["Aggregate_Routes"].append({})
        self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Destination"] = self.name_number[destination]["AS_Name"]
        self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Final_RTT"] = self.rtt[destination]
        self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["ISP_RTT"] = self.rtt[boundary]
        self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Aggregate_Route"] = []

    def addAggregateRoute(self, aggregate_routes_index, source, destination):
        self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Aggregate_Route"].append({})
        self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Aggregate_Route"][-1]["Name"] = self.name_number[source]["AS_Name"]
        self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Aggregate_Route"][-1]["lat"] = self.location[source][0]
        self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Aggregate_Route"][-1]["lng"] = self.location[source][1]
        self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Aggregate_Route"].append({})
        self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Aggregate_Route"][-1]["Name"] = self.name_number[destination]["AS_Name"]
        self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Aggregate_Route"][-1]["lat"] = self.location[destination][0]
        self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Aggregate_Route"][-1]["lng"] = self.location[destination][1]
        self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Traceroutes"] = []

    def addTraceroutes(self, aggregate_routes_index, destination, boundary):

        try:
            if self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index].has_key("Traceroutes"):
                self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Traceroutes"].append([])
            else:
                self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Traceroutes"] =[]

     #       if self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Traceroutes"] == []:
     #           self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Traceroutes"].append([])


            try:
                if self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Traceroutes"]:
                        self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Traceroutes"].append(self.rtt[boundary])
                        self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Traceroutes"].append(self.rtt[destination])
                else:
                    self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Traceroutes"] =  [self.rtt[boundary]]
                    self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Traceroutes"].append(self.rtt[destination])
            except IndexError:
                print "Index error"


            self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Traceroutes"].append([])
            for details_index in range(0, len(self.name_number)):
                if self.name_number[details_index]["AS_Name"] != "Private or unknown":
                    self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Traceroutes"][-1].append({})
                    self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Traceroutes"][-1][-1]["Name"] = self.name_number[details_index]["AS_Name"]
                    self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Traceroutes"][-1][-1]["RTT"] = self.rtt[details_index]
                    if self.location[details_index] == []:
                        self.location[details_index] = [0, 0]
                    self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Traceroutes"][-1][-1]["lat"] = self.location[details_index][0]
                    self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Traceroutes"][-1][-1]["lng"] = self.location[details_index][1]
        except:
            exc_info = sys.exc_info()
            traceback.print_exc()
            print "Exception in NetworkPerformance:AddTraceroutes", exc_info


    def creating(self):
        boundary = 0
        destination = 0
        traceroute_present = -1
        for details_index in range(0, len(self.name_number)):
            if self.name_number[details_index]["is_source"] == True:
                source = details_index
            if self.name_number[details_index]["is_destination"] == True:
                destination = details_index
            elif details_index == (len(self.name_number) - 1):
                destination = details_index
            if self.name_number[details_index]["is_boundary"] == True:
                boundary = details_index

        if destination != 0:
            traceroute_present = self.traceroutePresent(destination)
        else:
            pass

        if traceroute_present == -1: # No traceroute
            try:
                self.addAggregateRoutes(traceroute_present, destination, boundary)
                self.addAggregateRoute(traceroute_present, source, destination)
            except:
                pass
        if (boundary != 0) and (traceroute_present != -1):
            self.addTraceroutes(traceroute_present, destination, boundary)

        return self.network_dictionary