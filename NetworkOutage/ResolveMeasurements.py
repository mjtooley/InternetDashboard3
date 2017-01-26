from IPy import IP
from ipwhois import IPWhois
from ripe.atlas.sagan import PingResult
from ripe.atlas.cousteau import Probe
import pygeoip
import re
from GetMeasurements import Get

class Resolve(object):
    """
    This class is used to find the AS Name and probe details using the ping measurement.
    """

    def __init__(self, this_result, list):
        """
        Initialize the class.
        :param this_result:
        """
        self.this_result = this_result
        self.ip_address = self.this_result["from"]
        self.client = IPWhois(self.ip_address)
        self.probe_list = list

    def resolveMeasurements(self):
        """
        This function finds the AS Name using the source IP Address and returns the AS_Name.
        :return as_name:
        """
        try:
            as_name = 'none' # default
            gi_asn = pygeoip.GeoIP('GeoIPASNum.dat')
            asn_name = gi_asn.asn_by_addr(self.ip_address)

            if asn_name:
                names = str(asn_name).split()
                try:
                    asn = int(re.sub('[^0-9]', '', names[0]))  # Parse out the leadign number
                except:
                    pass
                del names[0]  #
                as_name = ' '.join(names)  # Re-assemble the ASN Name withouth the leading number

            ## ip_details = self.client.lookup_whois(self.ip_address)
            ## as_name = ip_details["nets"][0]["description"]
            ping_result = PingResult(self.this_result)
            # probe = Probe(id=ping_result.probe_id)
            if ping_result.probe_id not in self.probe_list:
                probes = Get() # Get the probe details from the DB instead of querying RIPE
                probe = probes.getProbe(ping_result.probe_id)
            else:
                probe = self.probe_list[ping_result.probe_id]

            asn = probe["asn"]
            return asn, as_name, ping_result, probe
        except Exception as e:
            print e




