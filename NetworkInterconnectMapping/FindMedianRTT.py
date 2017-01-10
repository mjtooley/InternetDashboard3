class FindMedianRTT(object):
    """
    This class is used to find the Median RTT per hop for each measurement.
    """
    def __init__(self, single_measurement):
        """
        Initialize the class.
        :param single_measurement:
        """

        self.single_measurement = single_measurement
        self.total_hops = len(self.single_measurement["result"])

    def findMedianRTT(self):
        """
        This function finds the Median RTT per hop for each measurement and returns a list of per hop Median RTTs.
        :return: all_rtts:
        """
        # List to store the per hop Median RTTs for each measurement
        all_rtts = []
        # Iterate through all the hops in each measurement
        for hopnumber in range(0, self.total_hops):
            # List to store the RTT values for the 3 packets sent in a hop
            per_hop_rtts = []
            # Default value of 0 if all 3 packets in a hop are lost
            per_hop_median_rtt = 0
            try:
                # Iterate through the 3 packets to get the RTT value from each packet
                for packetnumber in range(0, 3):
                    # Check if the key "rtt" is present in the data and append the value to the per_hop_rtts list
                    # Else append 0 to the per_hop_rtts list if the packet is lost
                    if "rtt" in self.single_measurement["result"][hopnumber]["result"][packetnumber]:
                        rtt = self.single_measurement["result"][hopnumber]["result"][packetnumber]["rtt"]
                        per_hop_rtts.append(rtt)
                    elif "x" in (self.single_measurement["result"][hopnumber]["result"][packetnumber]):
                        per_hop_rtts.append(0)
                # Iterate through the per_hop_rtts list and add the values
                for packet_rtt in per_hop_rtts:
                    per_hop_median_rtt += packet_rtt
                # Check if there are any 0's in per_hop_rtts
                while (0 in per_hop_rtts):
                    # If per_hop_rtts == 0 and length == 1, stop
                    # Else, remove the zeros present in the list
                    if (len(per_hop_rtts) == 1) and (0 in per_hop_rtts):
                        break
                    else:
                        per_hop_rtts.remove(0)
                # Find the Median RTT per hop
                per_hop_median_rtt = per_hop_median_rtt / len(per_hop_rtts)
                # Append the Median RTT per hop to the all_rtts list
                all_rtts.append(per_hop_median_rtt)
            except:
                pass
        return all_rtts