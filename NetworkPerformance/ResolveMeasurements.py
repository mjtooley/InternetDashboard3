from ipwhois import IPWhois
from IPy import IP
from pprint import pprint
import sys
import traceback
import pygeoip
import re

class Resolve(object):
    """
    This class is used to find the AS Name and ASN using the IP Address at each hop of each traceroute measurement and find the network connected to the source network.
    """
    def __init__(self, ip_path, as_number):
        """
        Initialize the class.
        :param ip_path:
        :param as_number:
        """
        self.ip_path = ip_path
        self.as_number = as_number
        self.is_present = False

    # def sourceName(self, source_ip):
    #     client = IPWhois(source_ip)
    #     source_details = client.lookup_whois()
    #     return source_details["nets"][0]["description"]

    # def changeKeys(self, neighbor_networks):
    #     neighbor_networks[1]["Destination_ASN"] = neighbor_networks[1]["Neighbor_ASN"]
    #     neighbor_networks[1]["Destination_AS_Name"] = neighbor_networks[1]["Neighbor_AS_Name"]
    #     neighbor_networks[2]["Source_ASN"] = neighbor_networks[2]["ASN"]
    #     neighbor_networks[2]["Source_AS_Name"] = neighbor_networks[2]["AS_Name"]
    #     neighbor_networks[1].pop("Neighbor_ASN")
    #     neighbor_networks[1].pop("Neighbor_AS_Name")
    #     neighbor_networks[2].pop("ASN")
    #     neighbor_networks[2].pop("AS_Name")
    #
    #     return neighbor_networks

    def resolveMeasurements(self):
        previous_or_next = []
        neighbor_networks = []
        switch_to_name = False
        is_destination = False
        index = 0

        for ip_address in self.ip_path:
            is_boundary = False
            is_source = True
            hopnumber = index
            # hopnumber = self.ip_path.index(ip_address)
            if hopnumber == len(self.ip_path) - 1:
                self.is_present = False
                is_destination = True
                switch_to_name = True
            in_private = IP(ip_address)
            if in_private.iptype() != "PRIVATE":
                #client = IPWhois(ip_address)
                #ip_details = client.lookup_whois()
                #if not switch_to_name:
                #    as_name = ip_details["nets"][0]["description"]
                #else:
                #    as_name = ip_details["nets"][0]["name"]
                #asn = ip_details["asn"]

                gi_asn = pygeoip.GeoIP('GeoIPASNum.dat')
                as_name = gi_asn.asn_by_addr(ip_address)
                if as_name:
                    names = str(as_name).split()
                    try:
                        asn = int(re.sub('[^0-9]', '', names[0])) # Parse out the leadign number
                    except:
                        pass
                    del names[0]  #
                    as_name = ' '.join(names) # Re-assemble the ASN Name withouth the leading number
                else:
                    #asn = 0
                    #as_name = 'Private'
                    continue

            elif in_private.iptype() == "PRIVATE":
                is_source = False
                as_name = "Private or unknown"
                asn = "Private or unknown"
            else:
                continue
            previous_or_next.append({})
            previous_or_next[-1]["AS_Name"] = as_name
            previous_or_next[-1]["ASN"] = asn

            for network_index in range(0, len(neighbor_networks)):
                if neighbor_networks[network_index]["is_source"] == True:
                    is_source = False
                    break

            neighbor_networks.append({})
            neighbor_networks[-1]["AS_Name"] = as_name
            neighbor_networks[-1]["ASN"] = asn
            neighbor_networks[-1]["Hopnumber"] = hopnumber
            neighbor_networks[-1]["is_boundary"] = is_boundary
            neighbor_networks[-1]["is_source"] = is_source
            neighbor_networks[-1]["is_destination"] = is_destination

            # if add_source and neighbor_networks == []:
            #     source = previous_or_next[-1]
            #     # neighbor_networks[-1]["Source_ASN"] = asn
            #     # neighbor_networks[-1]["Source_AS_Name"] = as_name
            #     source["Hopnumber"] = hopnumber
            #     add_source = False

            if len(previous_or_next) == 2:
                boundary = self.findBoundary(previous_or_next, hopnumber)
                previous_or_next.reverse()
                previous_or_next.pop()
                if boundary != None:
                    is_boundary = True
                    for network_index in range(0, len(neighbor_networks)):
                        if neighbor_networks[network_index]["is_boundary"] == True:
                            is_boundary = False
                            break
                    neighbor_networks[-1]["is_boundary"] = is_boundary
            index += 1
        #             for neighbor_index in range(0, len(neighbor_networks)):
        #                 if neighbor["Neighbor_ASN"] == neighbor_networks[neighbor_index]["Neighbor_ASN"]:
        #                     self.is_present = True
        #             if not self.is_present:
        #                 # pprint(ip_details)
        #                 neighbor_networks.append(neighbor)
        #                 self.is_present = True
        # neighbor_networks.append(source)
        return neighbor_networks


    def findBoundary(self, two_hops, hopnumber):
        # neighbors = {}
        try:
            if two_hops[1]["ASN"] is None:
                return

            if isinstance(two_hops[1]["ASN"],int):
                if (int(two_hops[1]["ASN"]) == self.as_number): #("Private" in two_hops[0]["ASN"]) or
                    return
            else:
                try:
                    if ( "Private" in two_hops[1]["ASN"] ) :
                        return
                except:
                    pass
                try:
                    if ("NA" in two_hops[1]["ASN"]):
                        return
                except:
                    pass

            if (two_hops[0]["AS_Name"] != two_hops[1]["AS_Name"]) and (two_hops[0]["ASN"] != two_hops[1]["ASN"]):
                return hopnumber
        except:
            exc_info = sys.exc_info()
            print "Exception in NetworkPerformance:", exc_info
            traceback.print_exc()
            return