import pyasn
import pygeoip
import re
import maxminddb
from geoip import geolite2

ips = {'216.58.217.228', '23.236.62.147', '108.56.234.125' }
ip = '23.236.62.147'

#asndb = pyasn.pyasn('ipasn_20150224.dat')

#asn = asndb.lookup(ip)
#print asn

gi = pygeoip.GeoIP('GeoIPOrg.dat')
owner = gi.org_by_addr(ip)

gi_asn = pygeoip.GeoIP('GeoIPASNum.dat')

asn_name = gi_asn.asn_by_addr(ip)

names = str(asn_name).split()

asn = int(re.sub('[^0-9]','',names[0]))

del names[0] #
name = ''
owner = ' '.join(names)
for name in names:
    owner += name

print owner

#r eader = maxminddb.open_database("GeoLite2-City.mmdb")

#location = reader.get(ip)

match = geolite2.lookup(ip)
location = match.location

print location

