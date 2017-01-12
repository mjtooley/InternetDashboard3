from geoip import geolite2

def getLocation(ip):
    latitude_longitude = []
    ip_info = geolite2.lookup(ip)
    if ip_info is None:
        return 38.0,-97.0
    else:
        return ip_info.location[0],ip_info.location[1]