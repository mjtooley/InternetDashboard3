from cymruwhois import Client
from IPy import IP
import pygeoip
import re

# from ipwhois import IPWhois
from ipwhois.utils import (ipv4_is_defined, ipv6_is_defined)
# from bulkwhois.cymru import BulkWhoisCymru

class Resolve(object):
    """
    This class is used to find the AS Name and ASN using the IP Address at each hop of each traceroute measurement
    and find the network connected to the source network. If the first hop measurement is a backbone network then
    find the network connected to the backbone network.
    """
    def __init__(self, ip_path, as_number, target_asns):
        """
        Initialize the class.
        :param ip_path:
        :param as_number:
        :param target_asns:
        """
        self.ip_path = ip_path
        self.as_number = as_number
        self.target = target_asns
        self.client = Client()
        # self.client = BulkWhoisCymru()
        self.is_present = False


    def resolveMeasurements(self):
        """
        This function finds the AS Name and ASN using IP Addresses and returns the AS Name, ASN and Hop number of the
        first and second neighbor network to the source network.
        :return neighbor_networks:
        """
        # Initialize a list to store the AS Names and ASNs of the two hops to be compared
        previous_or_next = []
        # Initialize a list to store the AS Name and ASN of the neighbor network(s) if found
        neighbor_networks = []

        # Iterate through the IP Addresses until a neighbor is found
        for ip_address in self.ip_path:
            # Store the hop number to add to neighbor_networks if a neighbor is found
            hopnumber = self.ip_path.index(ip_address)
            # Check if IP address in private IP Address space.
            in_private = IP(ip_address)
            if in_private.iptype() != "PRIVATE":
                # client = IPWhois(ip_address)
                # Get the AS Name and ASN from the IP Address at each hop
                gi_asn = pygeoip.GeoIP('GeoIPASNum.dat')
                asn_name = gi_asn.asn_by_addr(ip_address)
                if asn_name:
                    names = str(asn_name).split()
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

                # Pranav's original method below, worked but timed out on accoastion
                ##ip_details = self.client.lookup(ip_address)
                # Get the AS Name
                ##as_name = ip_details.owner
                ##asn = ip_details.asn

            # Check for exception if IP Address is private or no entry in cymruwhois database
            # if ((as_name == None) and (asn == None)) or ((as_name == "NA") and (asn == "NA")):
            else:
                continue

            # Append an empty dictionary to the previous_or_next list
            previous_or_next.append({})
            # Store the AS Name in the dictionary just appended to previous_or_next
            previous_or_next[-1]["AS_Name"] = as_name
            # Store the ASN in the dictionary just appended to previous_or_next
            previous_or_next[-1]["ASN"] = asn

            # Check if there are two hops to be compared in the previous_or_next list
            if len(previous_or_next) == 2:
                # Check if the network changes between the two hops
                neighbor = self.findBoundary(previous_or_next, hopnumber)
                # Reverse the previous_or_next list
                previous_or_next.reverse()
                # Pop the dictionary at previous_or_next[-1]
                # Reverse and pop is done to compare consecutive hops in the traceroute
                previous_or_next.pop()
                # Check to see if neighbor is found by findBoundary
                if neighbor != None:
                    # Iterate through the neighbor_networks list
                    for neighbor_index in range(0, len(neighbor_networks)):
                        # Check to see if the neighbor_found is already in the neighbor_networks list
                        # If present, set self.is_present to True
                        if neighbor["Neighbor_ASN"] == neighbor_networks[neighbor_index]["Neighbor_ASN"]:
                            self.is_present = True
                    # If neighbor found is not present in the neighbor_networks list, append it.
                    if not self.is_present:
                        neighbor_networks.append(neighbor)
                    # Check if the measurement is towards a specific target ASN
                    # If it is towards a target ASN, find all the network boundaries from the source ASN to the target
                    # ASN
                    if type(self.target) != int:
                        # If measurement is not towards a target ASN check if neighbor found is backbone network.
                        # If it is a backbone network, continue to find the neighbor of the backbone network. Else,
                        # stop.
                        if ("BACKBONE" not in neighbor["Neighbor_AS_Name"]):
                            if ("Backbone" not in neighbor["Neighbor_AS_Name"]):
                                break
        return neighbor_networks

    def findBoundary(self, two_hops, hopnumber):
        """
        This function is used to find the boundary by comparing AS Names and ASNs. It uses two_hops and hopnumber as
        arguments and returns either a dictionary or None depending if a boundary is found or not.
        :param two_hops:
        :param hopnumber:
        :return neighbors or None:
        """
        # Initialize an empty dictionary to store the AS Name, ASN and Hop number of the neighboring network
        neighbors ={}
        # Check to see if the ASN in the second value in two_hops is equal to the source ASN. If equal, return None
        # Else, check if the AS Names and ASNs of the values in two_hops are different and add the AS Name, ASN and
        # Hop number of the second value to the neighbors dictionary and return it
        if int(two_hops[1]["ASN"]) == self.as_number:
            return
        elif (two_hops[0]["AS_Name"] != two_hops[1]["AS_Name"]) and (two_hops[0]["ASN"] != two_hops[1]["ASN"]):
            neighbors["Neighbor_AS_Name"] = two_hops[1]["AS_Name"]
            neighbors["Neighbor_ASN"] = two_hops[1]["ASN"]
            neighbors["Hopnumber"] = hopnumber
            return neighbors