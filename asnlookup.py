import pygeoip
import re

class Asn:
    def __index__(self):
        self.asn = dict()
        self.asn['7922'] = 'Comcast'
        self.asn['22773'] = 'Cox'
        self.asn['20115'] = 'Charter'
        self.asn['6128'] = 'AlticeUSA'
        self.asn['30036'] = 'Mediacom'
        self.asn['10796'] = 'Charter'
        self.asn['11351'] = 'Charter'
        self.asn['11426'] = 'Charter'
        self.asn['11427'] = 'Charter'
        self.asn['12271'] = 'Charter'
        self.asn['20001'] = 'Charter'
        self.asn['19108'] = 'AlticeUSA'
        self.asn['7018'] = 'ATT'
        self.asn['20057'] = 'ATT'
        self.asn['701'] = 'Verizon'
        self.asn['702'] = 'Verizon'
        self.asn['22394'] = 'Verizon Wireless'
        self.asn['209'] = 'CenturyLink'
        self.asn['22561'] = 'CenturyLink'
        self.asn['26868'] = 'NCTA'
        self.asn['6939'] = 'Hurricane Electric'
        self.asn['174'] = 'Cogent'
        self.asn['3549'] = 'Level 3'
        self.asn['5650'] = 'Frontier'
        self.asn['11492'] = 'CableOne'

def getAsn(ip):
    as_name = 'none'  # default
    gi_asn = pygeoip.GeoIP('GeoIPASNum.dat')
    asn_name = gi_asn.asn_by_addr(ip)
    asn = None


    if asn_name:
        names = str(asn_name).split()
        try:
            asn = int(re.sub('[^0-9]', '', names[0]))  # Parse out the leadign number
        except:
            asn = None
        del names[0]  #
        as_name = ' '.join(names)  # Re-assemble the ASN Name withouth the leading number

    return asn, as_name

