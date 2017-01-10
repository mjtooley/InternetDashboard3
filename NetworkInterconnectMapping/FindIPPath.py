class Find(object):
    """
    This class is used to find the IP Path of each traceroute measurement.
    """
    def __init__(self, single_measurement):
        """
        Initialize the class.
        :param single_measurement:
        """
        self.single_measurement = single_measurement
        # Get the total number of hops in the traceroute
        self.total_hops = len(self.single_measurement["result"])

    def findIPPath(self):
        """
        This function finds the IP path of each traceroute measurement.
        :return:
        """
        # Initialize a list to store the IP Address of each hop in the traceroute
        ip_path = []
        # Iterate through all the hops in the traceroute
        for hopnumber in range(0, self.total_hops):
            try:
                # There are 3 packets per hop. Iterate through the packets per hop.
                # If an IP Address is found in the first packet itself, then stop and go to the next hop.
                # Else if it is not the last packet and the packet is lost, go to the next packet for the IP Address.
                # Continue until last packet if the first two packets are lost. If the last packet is also lost then
                # append 0.0.0.0 to the ip_path list
                for packetnumber in range(0, 3):
                    if "from" in self.single_measurement["result"][hopnumber]["result"][packetnumber]:
                        ip_address = self.single_measurement["result"][hopnumber]["result"][packetnumber]["from"]
                        ip_path.append(ip_address)
                        break
                    elif "x" in (self.single_measurement["result"][hopnumber]["result"][packetnumber]) and (packetnumber < 2):
                        continue
                    else:
                        ip_path.append("0.0.0.0")
            # If the raw data contains an error (e.g: traceroute did not complete) append 0.0.0.0 to the ip_path list
            except Exception:
                ip_path.append("0.0.0.0")

        return ip_path
