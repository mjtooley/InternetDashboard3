import json

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
        if self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Traceroutes"] == []:
            self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Traceroutes"].append([])
        self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Traceroutes"][0].append([])
        self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Traceroutes"][0][-1].append(self.rtt[boundary])
        self.network_dictionary["Networks"][-1]["Aggregate_Routes"][aggregate_routes_index]["Traceroutes"][0][-1].append(self.rtt[destination])

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

    def creating(self):
        for details_index in range(0, len(self.name_number)):
            if self.name_number[details_index]["is_source"] == True:
                source = details_index
            if self.name_number[details_index]["is_destination"] == True:
                destination = details_index
            elif details_index == (len(self.name_number) - 1):
                destination = details_index
            if self.name_number[details_index]["is_boundary"] == True:
                boundary = details_index

        traceroute_present = self.traceroutePresent(destination)

        if traceroute_present == -1:
            self.addAggregateRoutes(traceroute_present, destination, boundary)
            self.addAggregateRoute(traceroute_present, source, destination)
        self.addTraceroutes(traceroute_present, destination, boundary)

        return self.network_dictionary