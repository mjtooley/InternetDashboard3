import json
import urllib2
import traceback
import sys


class Creating(object):
    """
    This class is used to create a formatted JSON document to visualize the Network Interconnect map using D3.js.
    """

    def __init__(self, neighbor_dictionary, source, is_present, new_entry):
        """
        Initialize the class.
        The argument neighbor_dictionary is a dictionary with 4 keys - Nodes, Links, Backbone_AS_List and Source_List
        during initialization.
        The argument source is the source ASN.
        The argument is_present is used to check if a value is present in the Nodes list in the neighbor dictionary.
        And it is False by default.
        THe argument new_entry is used to check if a value is ????????????
        :param neighbor_dictionary:
        :param source:
        :param is_present:
        :param new_entry:
        """
        self.neighbor_dictionary = neighbor_dictionary
        self.source = source
        self.is_present = is_present
        self.new_entry = new_entry
        # Initialize a shared_by list to store the ASN of the neighbor connected to a network
        self.shared_by = []
        # self.addASList(neighbor_dictionary, source, self.getASName(source))
        # self.addSourceList(neighbor_dictionary, source, self.getASName(source))
        # Initialize source_present to False. source_present is used to check if the source ASN is already in the Nodes
        # list of the neighbor_dictionary
        source_present = False
        # Iterate through the Nodes list in the neighbor_dictionary
        for node_index in range(0, len(neighbor_dictionary["Nodes"])):
            # Check if the source ASN is already present at the current index in the Nodes list in
            # neighbor_dictionary
            if str(source) == str(neighbor_dictionary["Nodes"][node_index]["AS_Number"]):
                # If source ASN is already present in the Nodes list, change source_present to True
                source_present = True
                # Save the index of the source in the Nodes list in origin_index and stop
                # The value of the origin_index is used when adding to the Links list in the neighbor_dictionary
                self.origin_index = node_index
                break
        # Check if the source is in the Nodes list
        if not source_present:
            # If source is not present in the Nodes list, add it to the Nodes list
            self.addNodes(neighbor_dictionary, source, self.getASName(source), self.getASName(source), source, 0, True,
                          False, self.shared_by)
            # Save the index of the source in the Nodes list in origin_index
            # The value of the origin_index is used when adding to the Links list in the neighbor_dictionary
            self.origin_index = neighbor_dictionary["Nodes"].index(neighbor_dictionary["Nodes"][-1])

    def getASName(self, source_asn):
        """
        This function gets the AS Name from the ASN using the RIPE STAT.
        The argument source_asn is used to get the AS Overview data from RIPE STAT.
        Return the AS_Name.
        :param source_asn:
        :return source_as_name:
        """

        asn = {}
        asn['7922'] = 'Comcast'
        asn['22773'] = 'Cox'
        asn['20115'] = 'Charter'
        asn['6128'] = 'AlticeUSA'
        asn['30036'] = 'Mediacom'
        asn['10796'] = 'Charter'
        asn['11351'] = 'Charter'
        asn['11426'] = 'Charter'
        asn['11427'] = 'Charter'
        asn['12271'] = 'Charter'
        asn['20001'] = 'Charter'
        asn['19108'] = 'AlticeUSA'
        asn['7018'] = 'ATT'
        asn['20057'] = 'ATT'
        asn['701'] = 'Verizon'
        asn['702'] = 'Verizon'
        asn['22394'] = 'Verizon Wireless'
        asn['209'] = 'CenturyLink'
        asn['22561'] = 'CenturyLink'
        asn['26868'] = 'NCTA'
        asn['6939'] = 'Hurricane Electric'
        asn['174'] = 'Cogent'
        asn['3549'] = 'Level 3'
        asn['5650'] = 'Frontier'
        asn['11492'] = 'CableOne'

        if source_asn in asn:
            name = asn[source_asn]
        else:
            name = 'unknown'
        return name

        # Open the URL and get the AS Overview JSON file
        #source_as_name_prefix = "https://stat.ripe.net/data/as-overview/data.json?resource=AS%s" % source_asn
        #source_as_name_prefix = source_as_name_prefix.strip()
        #try:
        #    source_as_name_data = json.load(urllib2.urlopen(source_as_name_prefix))
            # Get the AS_Name from the JSON file
        #    source_as_name = source_as_name_data["data"]["holder"]
        #except Exception as e:
        #    print e, source_asn
        #    source_as_name = "unknown"
        #return source_as_name

    # def addASList(self, neighbor_dictionary, as_number, as_name):
    #     neighbor_dictionary["AS_List"].append({})
    #     neighbor_dictionary["AS_List"][-1]["AS_Number"] = as_number
    #     neighbor_dictionary["AS_List"][-1]["AS_Name"] = as_name
    #     return neighbor_dictionary

    def addBackboneASList(self, neighbor_dictionary, as_number, as_name):
        """
        This function adds the AS Name and ASN to the Backbone_AS_List in the neighbor_dictionary.
        The argument neighbor_dictionary is used to save the new entry in the Backbone_AS_List.
        The argument as_number is the ASN of the backbone network saved in the Backbone_AS_List.
        The argument as_name is the AS Name of the backbone network saved in the Backbone_AS_List.
        Return the neighbor_dictionary with the updated Backbone_AS_List.
        :param neighbor_dictionary:
        :param as_number:
        :param as_name:
        :return neighbor_dictionary:
        """
        # Append a new dictionary in the Backbone_AS_List and add the as_number and as_name to the newly appended
        # dictionary.
        neighbor_dictionary["Backbone_AS_List"].append({})
        neighbor_dictionary["Backbone_AS_List"][-1]["AS_Number"] = as_number
        neighbor_dictionary["Backbone_AS_List"][-1]["AS_Name"] = as_name
        return neighbor_dictionary

    def addNodes(self, neighbor_dictionary, as_number, as_name, source_as_name, source_as_number, value, is_source,
                 is_shared, shared_by):
        """
        This function adds the AS Name, ASN, Source AS Name, Source ASN, value, Source, Shared and Shared By in the
        Nodes list in the neighbor_dictionary. The AS's added to this list are the NODES.
        The argument neighbor_dictionary is used to save the new entry in the Nodes list.
        The argument as_number is the AS Name of the neighbor saved in the Nodes list.
        The argument as_name is the ASN of the neighbor saved in the Nodes list.
        The argument source_as_name is the AS Name of the source saved in the Nodes list.
        The argument source_as_number is the AS Number of the source saved in the Nodes list.
        The argument value is the number of neighbors connected to the NODE saved in the Nodes list. Default is 0.
        The argument is_source is a boolean value that indicates if the NODE is a source to another NODE in the Nodes
        list. Default is False.
        The argument is_shared is a boolean value that indicates if the NODE is shared between two other NODES in the
        Nodes list. Default is False.
        The argument shared_by is a list of ASNs of all the NODES that are connect to a NODE in the Nodes list.
        Return the neighbor_dictionary with the updated Nodes list.
        :param neighbor_dictionary:
        :param as_number:
        :param as_name:
        :param source_as_name:
        :param source_as_number:
        :param value:
        :param is_source:
        :param is_shared:
        :param shared_by:
        :return neighbor_dictionary:
        """
        # Append a new dictionary to the Nodes list and add the as_number, as_name, source_as_name, source_as_number,
        # value, is_source, is_shared and shared_by to the newly appended dictionary
        neighbor_dictionary["Nodes"].append({})
        neighbor_dictionary["Nodes"][-1]["AS_Number"] = str(as_number)
        neighbor_dictionary["Nodes"][-1]["AS_Name"] = as_name
        neighbor_dictionary["Nodes"][-1]["Source_AS_Name"] = source_as_name
        neighbor_dictionary["Nodes"][-1]["Source_AS_Number"] = source_as_number
        neighbor_dictionary["Nodes"][-1]["value"] = value
        neighbor_dictionary["Nodes"][-1]["Source"] = is_source
        neighbor_dictionary["Nodes"][-1]["Shared"] = is_shared
        neighbor_dictionary["Nodes"][-1]["Shared_By"] = shared_by
        return neighbor_dictionary

    def addLinks(self, neighbor_dictionary, source, source_AS, source_AS_Number, target, target_AS, target_AS_Number,
                 rtt):#, average_rtt, above_average):
        """
        This function adds the source, source_AS, source_AS_Number, target, target_AS, target_AS_Number, rtt in the
        Links list in the neighbor_dictionary. This list defines the connection between two Nodes.
        The argument neighbor_dictionary is used to save the new entry in the Links list.
        The argument source is the index of the source AS Node in the Nodes list.
        The argument source_AS is the AS Name of the source AS Node saved in the Links list.
        The argument source_AS_Number is the ASN of the source AS Node saved in the Links list.
        The argument target is the index of the Node connected to the source AS Node in the Nodes list.
        The argument target_AS is the AS Name of the Node connected to the source AS Node saved in the Links list.
        The argument target_AS_Number is the ASN of the Node connected to the source AS Node save in the Links list.
        The argument rtt is the round trip time in milliseconds between the two connected Nodes.
        Return the updated neighbor_dictionary with the updated Links list.
        :param neighbor_dictionary:
        :param source:
        :param source_AS:
        :param source_AS_Number:
        :param target:
        :param target_AS:
        :param target_AS_Number:
        :param rtt:
        :return neighbor_dictionary:
        """
        neighbor_dictionary["Links"].append({})
        neighbor_dictionary["Links"][-1]["source"] = source
        neighbor_dictionary["Links"][-1]["Source_AS_Name"] = source_AS
        neighbor_dictionary["Links"][-1]["Source_AS_Number"] = source_AS_Number
        neighbor_dictionary["Links"][-1]["target"] = target
        neighbor_dictionary["Links"][-1]["Target_AS_Name"] = target_AS
        neighbor_dictionary["Links"][-1]["Target_AS_Number"] = target_AS_Number
        neighbor_dictionary["Links"][-1]["RTT"] = rtt
        # neighbor_dictionary["Links"][-1]["Average_RTT"] = average_rtt
        # neighbor_dictionary["Links"][-1]["Above_Average"] = above_average
        return neighbor_dictionary

    def addSourceList(self, neighbor_dictionary, source, source_AS):
        """
        This function adds the source, source_AS in the Source_List in the neighbor_dictionary.
        The argument neighbor_dictionary is used to save the new entry in the Source_List.
        The argument source is the ASN of the source AS Node saved in the Source_List.
        The argument source_AS is the AS Name of the source AS Node saved in the Source_List.
        Return the updated neighbor_dictionary with the updated Source_List.
        :param neighbor_dictionary:
        :param source:
        :param source_AS:
        :return neighbor_dictionary:
        """
        neighbor_dictionary["Source_List"].append({})
        neighbor_dictionary["Source_List"][-1]["AS_Name"] = source_AS
        neighbor_dictionary["Source_List"][-1]["AS_Number"] = source
        return neighbor_dictionary

    def creatingJson(self, neighbor_details, all_median_rtts):#, all_average_median_rtts):
        """
        This function creates the final json file by adding new data to the neighbor_dictionary.
        The argument neighbor_details is the AS Names, ASNs and Hop numbers of all the boundaries found in the
        traceroute. This value is a dictionary that is returned from the resolveMeasurements() method in
        ResolveMeasurements.py.
        The argument all_median_rtts is the list of Median RTTs of each hop in the traceroute. This value is a list
        returned from the findMedianRTT() method in FindMedianRTT.py.
        Return the updated neighbor_dictionary.
        :param neighbor_details:
        :param all_median_rtts:
        :return neighbor_dictionary:
        """
        # Check to see if the there are any neighbors/boundaries
        if neighbor_details != []:
            # is_present, new_entry are boolean values used to check if a value in neighbor_details is already present
            # in the neighbor_dictionary
            # shared_by is and empty list used to store the ASN of the connected Node to be added in to the Nodes list
            # in the neighbor_dictionary
            # number_of_boundaries is an int value that specifies the number of boundaries found in the traceroute.
            # neighbor_details_index is set to 1 add the neighbor to the neighbor_dictionary if the number of neighbors/
            # boundaries is greater than 1. It is also used as an index to refer to the AS Name, ASN or the Hopnumber of
            # the particular neighbor in the neighbor_details list.
            self.is_present = False
            self.new_entry = True
            self.shared_by = []
            number_of_boundaries = len(neighbor_details) - 1
            neighbor_details_index = 1
            # congested = False
            # Calculate the Median RTT between the two neighbors
            try:
                median_rtt = round(abs(all_median_rtts[neighbor_details[0]["Hopnumber"] - 1] -
                                   all_median_rtts[neighbor_details[0]["Hopnumber"] - 2]), 2)
            except:
                exc_info = sys.exc_info()
                print "Exception in NetworkInterconnect:creatingjson", exc_info
                traceback.print_exc()
            # average_median_rtt = round(abs(all_average_median_rtts[neighbor_details[0]["Hopnumber"] - 1] -
            #                                all_average_median_rtts[neighbor_details[0]["Hopnumber"] - 2]), 2)
            # if median_rtt == 0:
            #     congested = True
            # else:
            #     congested = median_rtt > (5 * average_median_rtt)
            # Iterate through all the Nodes in the Nodes list
            for node in range(0, len(self.neighbor_dictionary["Nodes"])):
                # Check to see if a neighbor is already present in the Nodes list. If it is already present, set the
                # is_present value to True and stop
                if (neighbor_details[0]["Neighbor_AS_Name"] == self.neighbor_dictionary["Nodes"][node]["AS_Name"]) or \
                        (neighbor_details[0]["Neighbor_ASN"] == self.neighbor_dictionary["Nodes"][node]["AS_Number"]):
                    self.is_present = True
                    self.new_entry = False
                    # previous_as_index is used to refer to the current Node in the Nodes list if the number of
                    # neighbors/boundaries is greater than 1 i.e. the current Node is connected to another Node.
                    previous_as_index = node
                    break
            # Check if the neighbor is not present in the Nodes list
            if not self.is_present or self.new_entry:
                # Check if the source ASN is not in the shared_by list for the Neighbor/Boundary
                # Append the source ASN to the shared_by list if not present
                if self.neighbor_dictionary["Nodes"][self.origin_index]["AS_Number"] not in self.shared_by:
                    self.shared_by.append(self.neighbor_dictionary["Nodes"][self.origin_index]["AS_Number"])
                # Add the neighbor/boundary to the Nodes list of the neighbor_dictionary
                self.addNodes(self.neighbor_dictionary, neighbor_details[0]["Neighbor_ASN"], \
                              neighbor_details[0]["Neighbor_AS_Name"], \
                              self.neighbor_dictionary["Nodes"][self.origin_index]["AS_Name"], \
                              self.neighbor_dictionary["Nodes"][self.origin_index]["AS_Number"], \
                              0, False, False, self.shared_by)
                # Check if the ASN of the Node just added to the Nodes list is present in the Shared_By list of the
                # source Node (source Node is with respect to the Node just added) in the Nodes list.
                # Append the ASN to the Shared_By list of the source Node if not present.
                if self.neighbor_dictionary["Nodes"][-1]["AS_Number"] not in \
                        self.neighbor_dictionary["Nodes"][self.origin_index]["Shared_By"]:
                    self.neighbor_dictionary["Nodes"][self.origin_index]["Shared_By"].\
                        append(self.neighbor_dictionary["Nodes"][-1]["AS_Number"])
                # Increase the values of the Node just added and the source Node (source Node is with respect to the
                # Node just added) in the Nodes list
                self.neighbor_dictionary["Nodes"][-1]["value"] += 1
                self.neighbor_dictionary["Nodes"][self.origin_index]["value"] += 1
                # Add the Source-Neighbor connection to the Links list
                self.addLinks(self.neighbor_dictionary, self.origin_index, \
                              self.neighbor_dictionary["Nodes"][self.origin_index]["AS_Name"], \
                              self.neighbor_dictionary["Nodes"][self.origin_index]["AS_Number"], \
                              self.neighbor_dictionary["Nodes"].index(self.neighbor_dictionary["Nodes"][-1]), \
                              self.neighbor_dictionary["Nodes"][-1]["AS_Name"], \
                              self.neighbor_dictionary["Nodes"][-1]["AS_Number"], str(median_rtt))
                              #str(average_median_rtt), congested)
                # previous_as_index is used to refer to the current Node in the Nodes list if the number of
                # neighbors/boundaries is greater than 1 i.e. the current Node is connected to another Node.
                previous_as_index = self.neighbor_dictionary["Links"][-1]["target"]

            # Check if the Neighbor is already present in the Nodes list. Continue if present
            if (self.is_present or not self.new_entry):
                # Check if the Links list is not empty. If not empty, continue.
                # If empty, add the AS Name and ASN of the source to the Nodes list entry of the Neighbor.
                if len(self.neighbor_dictionary["Links"]) != 0:
                    # Iterate through the Links list
                    for link_index in range(0, len(self.neighbor_dictionary["Links"])):
                        # link_is_present is a boolean variable used to decide if the Source-Neighbor connection entry
                        # should be added to the Links list. Default is False.
                        link_is_present = False
                        # Check if the Source-Neighbor connection is present in the Links list.
                        # If present, set link_is_present to True and break
                        if ((self.neighbor_dictionary["Links"][link_index]["source"] == self.origin_index) and \
                            (self.neighbor_dictionary["Links"][link_index]["target"] == previous_as_index)):
                            link_is_present = True
                            break
                else:
                    link_is_present = False
                    self.neighbor_dictionary["Nodes"][previous_as_index]["Source_AS_Name"] = \
                        self.neighbor_dictionary["Nodes"][self.origin_index]["AS_Name"]
                    self.neighbor_dictionary["Nodes"][previous_as_index]["Source_AS_Number"] = \
                        self.neighbor_dictionary["Nodes"][self.origin_index]["AS_Number"]

                # Check to see if the link is present in the Links list. Add the Link, increase the values of both the
                # Source and the current Node in the corresponding entry in the Nodes list, set the 'Source' parameter
                # of the Source Node to True as it is connected to another Node. Since, the Node was already present in
                # the Nodes list, set the 'Shared' parameter of the Node in the Nodes list to True as it is now shared
                # between two different source AS's. Lastly, add the ASNs of the Source and current Node to the
                # 'Shared_By' lists of the current Node and Source Node respectively in the Nodes list.
                if (link_is_present != True):
                    self.addLinks(self.neighbor_dictionary, self.origin_index,
                                  self.neighbor_dictionary["Nodes"][self.origin_index]["AS_Name"],
                                  self.neighbor_dictionary["Nodes"][self.origin_index]["AS_Number"], previous_as_index,
                                  self.neighbor_dictionary["Nodes"][previous_as_index]["AS_Name"],
                                  self.neighbor_dictionary["Nodes"][previous_as_index]["AS_Number"], str(median_rtt))
                                  #, str(average_median_rtt), congested)
                    self.neighbor_dictionary["Nodes"][self.origin_index]["value"] += 1
                    self.neighbor_dictionary["Nodes"][self.origin_index]["Source"] = True
                    self.neighbor_dictionary["Nodes"][previous_as_index]["value"] += 1
                    self.neighbor_dictionary["Nodes"][previous_as_index]["Shared"] = True
                    self.neighbor_dictionary["Nodes"][previous_as_index]["Shared_By"].append(
                        self.neighbor_dictionary["Nodes"][self.origin_index]["AS_Number"])
                    self.neighbor_dictionary["Nodes"][self.origin_index]["Shared_By"].append(
                        self.neighbor_dictionary["Nodes"][previous_as_index]["AS_Number"])

            # Check to see if there are any more boundaries in neighbor_details
            while neighbor_details_index <= number_of_boundaries:
                # Usages of is_present, shared_by are same as explained in the previous instances of the same variables.
                # Reset the values back to their defaults.
                # backbone_present is used to decide if a Node should be added to the Backbone_AS_List. Default is False
                self.is_present = False
                self.new_entry = True
                self.shared_by = []
                backbone_present = False
                # congested = False
                # Calculate the Median RTT between the two neighbors
                median_rtt = round(abs(all_median_rtts[neighbor_details[neighbor_details_index]["Hopnumber"] - 1] -
                                       all_median_rtts[neighbor_details[neighbor_details_index]["Hopnumber"] - 2]), 2)
                # average_median_rtt = round(abs(all_average_median_rtts[neighbor_details[
                #                                                            neighbor_details_index]["Hopnumber"] - 1] -
                #                                all_average_median_rtts[neighbor_details[neighbor_details_index]
                #                                                        ["Hopnumber"] - 2]), 2)
                # if median_rtt == 0:
                #     congested = True
                # else:
                #     congested = median_rtt > (5 * average_median_rtt)
                # present_in_source_list = False

                # for source_list_index in range(0, len(self.neighbor_dictionary["Source_List"])):
                #     if str(neighbor_details[0]["Neighbor_ASN"]) == str(
                #             self.neighbor_dictionary["Source_List"][source_list_index]["Source_AS_Number"]):
                #         present_in_source_list = True
                #
                # if not present_in_source_list:
                #     self.addSourceList(self.neighbor_dictionary, neighbor_details[0]["Neighbor_ASN"],
                #                        neighbor_details[0]["Neighbor_AS_Name"])

                # Check to see if the Backbone_AS_List is empty
                if self.neighbor_dictionary["Backbone_AS_List"] != []:
                    # Iterate through the Backbone_AS_List, if not empty
                    for backbone_index in range(0, len(self.neighbor_dictionary["Backbone_AS_List"])):
                        # Check if the previous neighbor/boundary in neighbor_details is present in the Backbone_AS_List
                        if neighbor_details[neighbor_details_index - 1]["Neighbor_ASN"] == \
                                self.neighbor_dictionary["Backbone_AS_List"][backbone_index]["AS_Number"]:
                            #If true, change the value of backbone_present to True and break
                            backbone_present = True
                            break
                # Check if the previous neighbor/boundary is not present in the Backbone_AS_List and if it is a
                # backbone network.
                if not backbone_present and ("BACKBONE" in
                                                 neighbor_details[neighbor_details_index - 1]["Neighbor_AS_Name"]):
                    # If true, add the previous neighbor/boundary in neighbor_details to the Backbone_AS_List
                    self.addBackboneASList(self.neighbor_dictionary,
                                           neighbor_details[neighbor_details_index - 1]["Neighbor_ASN"],
                                           neighbor_details[neighbor_details_index - 1]["Neighbor_AS_Name"])
                    # Iterate through the Source_List.
                    for as_index in range(0, len(self.neighbor_dictionary["Source_List"])):
                        # Check if the previous neighbor/boundary is present in the Source_List. If the previous
                        # neighbor/boundary/node is a backbone network, it can only be present in the Backbone_AS_List
                        # and the Nodes list.
                        if str(neighbor_details[neighbor_details_index - 1]["Neighbor_ASN"]) == \
                                str(self.neighbor_dictionary["Source_List"][as_index]["AS_Number"]):
                            # If true, pop the previous neighbor/boundary/node from the Source_List
                            self.neighbor_dictionary["Source_List"].pop(as_index)
                # Iterate through the Nodes list
                for node in range(0, len(self.neighbor_dictionary["Nodes"])):
                    # Check if the current neighbor/boundary is in the Nodes list using the AS Name and ASN
                    if (neighbor_details[neighbor_details_index]["Neighbor_AS_Name"] ==
                            self.neighbor_dictionary["Nodes"][node]["AS_Name"] or
                                neighbor_details[neighbor_details_index]["Neighbor_ASN"] ==
                                self.neighbor_dictionary["Nodes"][node]["AS_Number"]):
                        # If true, change the value of is_present to True
                        self.is_present = True
                        self.new_entry = False
                        # Iterate through the Nodes list again to find the index of the previous neighbor/boundary which
                        # is now the source to the current neighbor/boundary.
                        for previous_as_node in range(0, len(self.neighbor_dictionary["Nodes"])):
                            # Check if the previous neighbor/boundary is in the Nodes list. If present, save its index
                            # in the Nodes list in previous_as_index and break.
                            if neighbor_details[neighbor_details_index - 1]["Neighbor_ASN"] == \
                                    self.neighbor_dictionary["Nodes"][previous_as_node]["AS_Number"]:
                                previous_as_index = previous_as_node
                                break
                        break

                # Check if the current neighbor is not present in the Nodes list
                if not self.is_present or self.new_entry:
                    # Check if the source ASN is not in the shared_by list for the Neighbor/Boundary
                    # Append the source ASN to the shared_by list if not present
                    if self.neighbor_dictionary["Nodes"][previous_as_index]["AS_Number"] not in self.shared_by:
                        self.shared_by.append(self.neighbor_dictionary["Nodes"][previous_as_index]["AS_Number"])
                    # Add the current neighbor/boundary to the Nodes list of the neighbor_dictionary
                    self.addNodes(self.neighbor_dictionary, neighbor_details[neighbor_details_index]["Neighbor_ASN"],
                                  neighbor_details[neighbor_details_index]["Neighbor_AS_Name"],
                                  self.neighbor_dictionary["Nodes"][previous_as_index]["AS_Name"],
                                  self.neighbor_dictionary["Nodes"][previous_as_index]["AS_Number"],
                                  0, False, False, self.shared_by)
                    # Check if the ASN of the Node just added to the Nodes list is present in the Shared_By list of the
                    # source Node (source Node is with respect to the Node just added) in the Nodes list.
                    # Append the ASN to the Shared_By list of the source Node if not present.
                    if self.neighbor_dictionary["Nodes"][-1]["AS_Number"] not in \
                            self.neighbor_dictionary["Nodes"][previous_as_index]["Shared_By"]:
                        self.neighbor_dictionary["Nodes"][previous_as_index]["Shared_By"].append(
                            self.neighbor_dictionary["Nodes"][-1]["AS_Number"])
                    # Increase the values of the Node just added and the source Node (source Node is with respect to the
                    # Node just added) in the Nodes list. Change the 'Source' parameter of the source Node to True.
                    self.neighbor_dictionary["Nodes"][-1]["value"] += 1
                    self.neighbor_dictionary["Nodes"][previous_as_index]["value"] += 1
                    self.neighbor_dictionary["Nodes"][previous_as_index]["Source"] = True
                    # Add the Source-Neighbor connection to the Links list
                    self.addLinks(self.neighbor_dictionary, previous_as_index,
                                  self.neighbor_dictionary["Nodes"][previous_as_index]["AS_Name"],
                                  self.neighbor_dictionary["Nodes"][previous_as_index]["AS_Number"],
                                  self.neighbor_dictionary["Nodes"].index(self.neighbor_dictionary["Nodes"][-1]),
                                  self.neighbor_dictionary["Nodes"][-1]["AS_Name"],
                                  self.neighbor_dictionary["Nodes"][-1]["AS_Number"], str(median_rtt))
                                  # str(average_median_rtt), congested)
                    # previous_as_index is used to refer to the current Node in the Nodes list if the current Node is
                    # connected to another Node. Store the index of the current Node in the Nodes list in
                    # previous_as_index using the 'target' parameter in the Links list entry just added.
                    previous_as_index = self.neighbor_dictionary["Links"][-1]["target"]

                # Check if the Neighbor is already present in the Nodes list. Continue if present
                if self.is_present or not self.new_entry:
                    # Iterate through the Links list
                    for link_index in range(0, len(self.neighbor_dictionary["Links"])):
                        # link_is_present is a boolean variable used to decide if the Source-Neighbor connection entry
                        # should be added to the Links list. Default is False.
                        link_is_present = False
                        # Check if the Source-Neighbor connection is present in the Links list.
                        # If present, set link_is_present to True and break
                        if ((self.neighbor_dictionary["Links"][link_index]["source"] == previous_as_index) and \
                            (self.neighbor_dictionary["Links"][link_index]["target"] == node)):
                            link_is_present = True
                            break

                    # Check to see if the link is present in the Links list. Add the Link, increase the values of both
                    # the Source and the current Node in the corresponding entry in the Nodes list, set the 'Source'
                    # parameter of the Source Node to True as it is connected to another Node. Since, the current Node
                    # was already present in the Nodes list, set the 'Shared' parameter of the current Node in the Nodes
                    # list to True as it is now shared between two different source AS's. Lastly, add the ASNs of the
                    # Source and current Node to the 'Shared_By' lists of the current Node and Source Node respectively
                    # in the Nodes list.
                    if (link_is_present != True):
                        self.addLinks(self.neighbor_dictionary, previous_as_index,
                                      self.neighbor_dictionary["Nodes"][previous_as_index]["AS_Name"],
                                      self.neighbor_dictionary["Nodes"][previous_as_index]["AS_Number"],
                                      node, self.neighbor_dictionary["Nodes"][node]["AS_Name"],
                                      self.neighbor_dictionary["Nodes"][node]["AS_Number"], str(median_rtt))
                                      #, str(average_median_rtt), congested)
                        self.neighbor_dictionary["Nodes"][previous_as_index]["value"] += 1
                        self.neighbor_dictionary["Nodes"][previous_as_index]["Source"] = True
                        self.neighbor_dictionary["Nodes"][node]["value"] += 1
                        self.neighbor_dictionary["Nodes"][node]["Shared"] = True
                        self.neighbor_dictionary["Nodes"][node]["Shared_By"].append(
                            self.neighbor_dictionary["Nodes"][previous_as_index]["AS_Number"])
                        self.neighbor_dictionary["Nodes"][previous_as_index]["Shared_By"].append(
                            self.neighbor_dictionary["Nodes"][node]["AS_Number"])
                        # previous_as_index is used to refer to the current Node in the Nodes list if the current Node is
                        # connected to another Node. Store the index of the current Node in the Nodes list in
                        # previous_as_index using the node variable in the for loop at line 380.
                        previous_as_index = node
                # Increment the neighbor_details_index to check if there are any more neighbors in neighbor_details and
                # if the while loop condition at line 321 is still True.
                neighbor_details_index += 1

            # Iterate through the Nodes list
            for node_index in range(0, len(self.neighbor_dictionary["Nodes"])):
                # The variable present_in_source_list is used to decide if a Node should be added to the Source_List.
                # Default is False.
                present_in_source_list = False
                # The Source_List defines all the Nodes which are connected to another Node as a source. To decide
                # whether a Node should be added to the Source_List, check if the 'Source' parameter of each Node in the
                # Nodes list is True or False.
                # If False, go to the next Node in the Nodes list.
                if self.neighbor_dictionary["Nodes"][node_index]["Source"] == False:
                    continue
                # If True
                elif (self.neighbor_dictionary["Nodes"][node_index]["Source"] == True):
                    # Iterate through the Source_List
                    for source_list_index in range(0, len(self.neighbor_dictionary["Source_List"])):
                        # Check if the Node is already in the Source_List
                        if str(self.neighbor_dictionary["Nodes"][node_index]["AS_Number"]) == \
                                str(self.neighbor_dictionary["Source_List"][source_list_index]["AS_Number"]):
                            # If True, change the value of present_in_source_list to True and break
                            present_in_source_list = True
                            break
                # Check if the Node is in the Source_List and is not a backbone network
                if not present_in_source_list and ("BACKBONE" not in
                                                       self.neighbor_dictionary["Nodes"][node_index]["AS_Name"]):
                    # If True, add the Node to the Source_List
                    self.addSourceList(self.neighbor_dictionary,
                                       self.neighbor_dictionary["Nodes"][node_index]["AS_Number"],
                                       self.neighbor_dictionary["Nodes"][node_index]["AS_Name"])


        return self.neighbor_dictionary