import json


class Merging(object):

    def __init__(self, final_dictionary, probe_dictionary):
        self.final_dictionary = final_dictionary
        self.probe_dictionary = probe_dictionary
        self.status = "UP"

    def getStatus(self, packets_sent, packets_received):
        percent = float(packets_received)/float(packets_sent) * 100
        if percent <= 70.0:
            self.status = "DOWN"

        return percent

    def mergingJson(self):
        asn_present = True

        if self.final_dictionary == []:
            self.final_dictionary = self.probe_dictionary
            return self.final_dictionary

        for as_list_index_probe in range(0, len(self.probe_dictionary["AS_List"])):
            for as_list_index_final in range(0, len(self.final_dictionary["AS_List"])):
                if self.probe_dictionary["AS_List"][as_list_index_probe]["Name"] == self.final_dictionary["AS_List"][as_list_index_final]["Name"]:
                    if self.probe_dictionary["AS_List"][as_list_index_probe]["ASN"][0] not in self.final_dictionary["AS_List"][as_list_index_final]["ASN"]:
                        asn_present = False
                        break
                else:
                    self.final_dictionary["AS_List"].append(self.probe_dictionary["AS_List"][as_list_index_probe])
                    break

        if not asn_present:
            self.final_dictionary["AS_List"][as_list_index_final]["ASN"].append(self.probe_dictionary["AS_List"][0]["ASN"][0])

        for probes_index_probe in range(0, len(self.probe_dictionary["Probes"])):
            for probes_index_final in range(0, len(self.probe_dictionary["Probes"])):
                if (self.probe_dictionary["Probes"][probes_index_probe]["Lat"] ==
                        self.final_dictionary["Probes"][probes_index_final]["Lat"]) and \
                        (self.probe_dictionary["Probes"][probes_index_probe]["Long"] ==
                             self.final_dictionary["Probes"][probes_index_final]["Long"]):
                    self.final_dictionary["Probes"][probes_index_final]["received"] += self.probe_dictionary["Probes"][probes_index_probe]["received"]
                    self.final_dictionary["Probes"][probes_index_final]["sent"] += self.probe_dictionary["Probes"][probes_index_probe]["sent"]
                    self.getStatus(self.final_dictionary["Probes"][probes_index_final]["sent"], self.final_dictionary["Probes"][probes_index_final]["received"])
                    self.final_dictionary["Probes"][probes_index_final]["Status"] = self.status
                    break
                else:
                    self.final_dictionary["Probes"].append(self.probe_dictionary["Probes"][probes_index_probe])
                    break

        return self.final_dictionary