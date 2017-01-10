import json
import geocoder
import geoip2.database

class Creating(object):
    """
    This class is used to create a formatted JSON document to visualize the Network Outage map using D3.js.
    """

    def  __init__(self, probe_dictionary, resolved_measurement):
        self.probe_dictionary = probe_dictionary
        self.resolved_measurement = resolved_measurement
        self.probe_present = False
        self.asn_present = False
        self.status = "UP"

    def add_AS_List(self):
        self.probe_dictionary["AS_List"].append({})
        self.probe_dictionary["AS_List"][-1]["ASN"] = []
        self.probe_dictionary["AS_List"][-1]["Name"] = self.resolved_measurement[1]
        self.probe_dictionary["AS_List"][-1]["ASN"].append(self.resolved_measurement[0])

        return self.probe_dictionary

    def addProbes(self, latitude, longitude, packets_sent, packets_received):
        self.probe_dictionary["Probes"].append({})
        self.probe_dictionary["Probes"][-1]["AS_Number"] = self.resolved_measurement[0]
        self.probe_dictionary["Probes"][-1]["Lat"] = latitude
        self.probe_dictionary["Probes"][-1]["Long"] = longitude
        self.probe_dictionary["Probes"][-1]["network_name"] = self.resolved_measurement[1]
        self.probe_dictionary["Probes"][-1]["sent"] = packets_sent
        self.probe_dictionary["Probes"][-1]["received"] = packets_received
        self.probe_dictionary["Probes"][-1]["Packets_received"] = 100
        self.probe_dictionary["Probes"][-1]["Status"] = self.status
        self.probe_dictionary["Probes"][-1]["state"] = self.getState(latitude, longitude)
        return self.probe_dictionary

    def getStatus(self, packets_sent, packets_received):
        percent = float(packets_received)/float(packets_sent) * 100
        if percent <= 70.0:
            self.status = "DOWN"

        return percent

    def getState(self, latitude, longitude):
        try:
            location_from_coordinates = geocoder.arcgis([latitude, longitude], method="reverse")
            state_name = location_from_coordinates.state
        except Exception as e:
            state_name = None
            print e

        return state_name

    def checkNetworkName(self, probe_dictionary):
        for probe_index in range(0, len(probe_dictionary["Probes"])):
            for as_list_index in range(0, len(probe_dictionary["AS_List"])):
                if (probe_dictionary["Probes"][probe_index]["AS_Number"] in
                        probe_dictionary["AS_List"][as_list_index]["ASN"]) and \
                        (probe_dictionary["Probes"][probe_index]["network_name"] !=
                             probe_dictionary["AS_List"][as_list_index]["Name"]):
                    probe_dictionary["Probes"][probe_index]["network_name"] = \
                    probe_dictionary["AS_List"][as_list_index]["Name"]
                    break
        return probe_dictionary

    def creatingJson(self):
        try:
            longitude = self.resolved_measurement[3].geometry["coordinates"][0]
            latitude = self.resolved_measurement[3].geometry["coordinates"][1]
        except Exception as e:
            print e
        packets_sent = self.resolved_measurement[2].packets_sent
        packets_received = self.resolved_measurement[2].packets_received

        for probe_index in range(0, len(self.probe_dictionary["Probes"])):
            if (latitude == self.probe_dictionary["Probes"][probe_index]["Lat"]) \
                    and (longitude == self.probe_dictionary["Probes"][probe_index]["Long"]):
                self.probe_present = True
                self.probe_dictionary["Probes"][probe_index]["sent"] += packets_sent
                self.probe_dictionary["Probes"][probe_index]["received"] += packets_received
                self.probe_dictionary["Probes"][probe_index]["Packets_received"] = \
                    self.getStatus(self.probe_dictionary["Probes"][probe_index]["sent"],
                                   self.probe_dictionary["Probes"][probe_index]["received"])
                self.probe_dictionary["Probes"][probe_index]["Status"] = self.status
                break
        if not self.probe_present:
            self.getStatus(packets_sent, packets_received)
            self.addProbes(latitude, longitude, packets_sent, packets_received)

        for as_list_index in range(0, len(self.probe_dictionary["AS_List"])):
            if (self.resolved_measurement[1] == self.probe_dictionary["AS_List"][as_list_index]["Name"]) and \
                    (self.resolved_measurement[0] in self.probe_dictionary["AS_List"][as_list_index]["ASN"]):
                self.asn_present = True
                break
            elif (self.resolved_measurement[1] == self.probe_dictionary["AS_List"][as_list_index]["Name"]):
                if self.resolved_measurement[0] not in self.probe_dictionary["AS_List"][as_list_index]["ASN"]:
                   self.probe_dictionary["AS_List"][as_list_index]["ASN"].append(self.resolved_measurement[0])
                   self.asn_present = True
                   break
            elif (self.resolved_measurement[1] != self.probe_dictionary["AS_List"][as_list_index]["Name"]) and \
                    (self.resolved_measurement[0] in self.probe_dictionary["AS_List"][as_list_index]["ASN"]):
                self.asn_present = True
                break
            else:
                self.asn_present = False

        if not self.asn_present:
            self.add_AS_List()
        return self.probe_dictionary

