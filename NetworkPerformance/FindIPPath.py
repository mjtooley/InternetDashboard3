import geocoder
import maxminddb
from geoip import geolite2

class Find(object):
    """
    This class is used to find the IP Path of each traceroute measurement.
    """
    def __init__(self, single_measurement):
        """
        Initialize the class
        :param single_measurement:
        """
        # self.reader = maxminddb.open_database("/home/ncta/InternetDashboard/GeoLite2-City.mmdb")
        self.single_measurement = single_measurement
        self.total_hops = len(self.single_measurement["result"])

    def checkHop(self, hop):
        hop_ip_address = []
        hop_rtt = []

        for packetnumber in range(0, 3):
            if "from" in hop[packetnumber]:
                hop_ip_address.append(hop[packetnumber]["from"])

                if "rtt" in hop[packetnumber]:
                    hop_rtt.append(hop[packetnumber]["rtt"])

            elif "x" in hop[packetnumber]:
                pass

        if len(hop_ip_address) == 2:
            if hop_ip_address[0] != hop_ip_address[1]:
                hop_ip_address.pop()
                hop_rtt.pop()
        elif len(hop_ip_address) == 3:
            if ((hop_ip_address[0] != hop_ip_address[1]) and (hop_ip_address[1] == hop_ip_address[2])) or \
                    ((hop_ip_address[0] != hop_ip_address[1]) and (hop_ip_address[1] != hop_ip_address[2])):
                del hop_ip_address[1:]
                del hop_rtt[1:]
            elif ((hop_ip_address[0] == hop_ip_address[2]) and (hop_ip_address[0] != hop_ip_address[1])):
                del hop_ip_address[1:2]
                del hop_rtt[1:2]
            elif ((hop_ip_address[0] == hop_ip_address[1]) and (hop_ip_address[1] != hop_ip_address[2])):
                hop_ip_address.pop()
                hop_rtt.pop()
        elif len(hop_ip_address) == 0:
            hop_ip_address = ["0.0.0.0"]
            hop_rtt = [0]
        median_hop_rtt = sorted(hop_rtt)[len(hop_rtt) // 2]

        return hop_ip_address[0], median_hop_rtt

    def findLocation(self, ip_address):
        latitude_longitude = []
        #ip_location = self.reader.get(ip_address)
        ip_info = geolite2.lookup(ip_address)

        if ip_info is not None:
            ip_location = ip_info.location
            latitude_longitude.append(ip_location[0]) #Latitude
            latitude_longitude.append(ip_location[1]) #Longitude
        return latitude_longitude

    def findIPPath(self):

        ip_path = []
        locations = []
        median_rtts = []

        for hopnumber in range(0, self.total_hops):
            if "result" in self.single_measurement["result"][hopnumber]:
                try:
                    checkedHop = self.checkHop(self.single_measurement["result"][hopnumber]["result"])
                    ip_path.append(checkedHop[0])
                    median_rtts.append(checkedHop[1])
                    getLocation = self.findLocation(checkedHop[0])
                    locations.append(getLocation)
                except:
                    pass


        return ip_path, locations, median_rtts

    # def findIPPath(self):
    #     """
    #     This function finds the IP path of each traceroute measurement.
    #     :return:
    #     """
    #     ip_path = []
    #     locations = []
    #     rtts = []
    #     for hopnumber in range(0, self.total_hops):
    #         rtts.append([])
    #         try:
    #             for packetnumber in range(0, 3):
    #                 if "from" in self.single_measurement["result"][hopnumber]["result"][packetnumber]:
    #                     ip_address = self.single_measurement["result"][hopnumber]["result"][packetnumber]["from"]
    #                     rtts[hopnumber].append(self.single_measurement["result"][hopnumber]["result"][packetnumber]["rtt"])
    #                     if (ip_address not in ip_path):
    #                         # if (ip_path == []) or (ip_address == self.single_measurement["result"][hopnumber]["result"][packetnumber - 1]["from"]):
    #                         if (packetnumber != 0) and ("from" in self.single_measurement["result"][hopnumber]["result"][packetnumber - 1]) and \
    #                                 (ip_address != self.single_measurement["result"][hopnumber]["result"][packetnumber - 1]):
    #                             continue
    #                         ip_path.append(ip_address)
    #                         latitude_longitude = []
    #                         ip_location = self.reader.get(ip_address)
    #                         if ip_location != None:
    #                             latitude_longitude.append(ip_location["location"]["latitude"])
    #                             latitude_longitude.append(ip_location["location"]["longitude"])
    #                         # location = geocoder.ip(str(ip_address))
    #                         locations.append(latitude_longitude)
    #                 elif "x" in (self.single_measurement["result"][hopnumber]["result"][packetnumber]) and (packetnumber < 2):
    #                     rtts[hopnumber].append(0)
    #                     continue
    #                 else:
    #                     rtts[hopnumber].append(0)
    #                     if len(ip_path) != hopnumber + 1:
    #                         ip_path.append("0.0.0.0")
    #                         latitude_longitude = []
    #                         ip_location = self.reader.get(ip_address)
    #                         latitude_longitude.append(ip_location["location"]["latitude"])
    #                         latitude_longitude.append(ip_location["location"]["longitude"])
    #                         # location = geocoder.ip(str(ip_address))
    #                         locations.append(latitude_longitude)
    #         except Exception as e:
    #             print e
    #             rtts[hopnumber].append(0)
    #             ip_path.append("0.0.0.0")
    #         rtts[hopnumber] = sorted(rtts[hopnumber])[len(rtts[hopnumber]) // 2]
    #
    #     return ip_path, locations, rtts