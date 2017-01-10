"""
This file is to get the traceroute results originating from ISP ASNs to a target ASN from RIPE Atlas servers and store
those results in MongoDB.
"""

from pymongo import MongoClient
from ripe.atlas.cousteau import AtlasResultsRequest, AtlasLatestRequest, ProbeRequest, MeasurementRequest

# Connect to the database using pymongo. No arguments to MongoClient() connects to the localhost at port 27017.
# Else, connect to the database at the specified IP address and port number
client = MongoClient()#"172.25.11.132", 27017)
# Specify the database name at that IP address. (Database Name = AllASNsTWCOutage)
db = client.AllASNsTWCOutage

# Source Network - ASN(s)
# Comcast - 7922
# Cox - 22773
# Charter - 20115
# Cablevision - 6128
# Mediacom - 30036
# TWC - 10796, 11351, 11426, 11427, 12271, 20001
# Suddenlink - 19108
# ATT - 7018, 20057
# Verizon - 701, 702
# Verizon Wireless - 22394
# CenturyLink - 209, 22561
# NCTA - 26868
# Hurricane - 6939
# Cisco - 109, 3943
# Cogent - 174
# Energy Sciences Network - 292
# Internet Systems Consortium - 1280
# NTT Communications - 2914
# Level 3 - 3549
# Frontier Communications - 5650
# TW Telecom - 4323
# Hughes - 6621
# Sonoma Interconnect - 7065
# ViaSat - 7155
# CableOne - 11492
# San Franscisco Metropolitan Internet Exchange - 12276
# Google Fiber - 16591
# Louisiana Optical Network Initiative - 32440
# Bright House Networks - 33363
# Yelp - 33445
# OpenDNS - 36692
# Cloudfare - 394536
# Northland Cable TV - 40285

# Create a list of ASNs from which the measurement originates
list_of_source_asns = [7922, 22773, 20115, 6128, 30036, 10796, 11351, 11426, 11427, 12271, 20001, 19108, 7018, 20057, \
                       701, 22394, 209, 22561, 26868, 6939, 109, 3943, 174, 292, 1280, 2914, 3549, 5650, 4323, 6621, \
                       7065, 7155, 11492, 12276, 16591, 32440, 33363, 33445, 36692, 394536, 40285]

# Target Network - ASN(s)
# Facebook - 32934, 54115, 63293
# Amazon - 7224, 14618, 16509
# Netflix - 40027
# Google - 15169, 22589, 36039, 36384
# Google Fiber - 19448
# Twitter - 13414, 35995, 54888
# Youtube - 36040, 36561, 43515

# target_asns is used to find results from the database Internet_Dashboard/interconnects, if measurements going to
# Google, Facebook, Amazon, Netflix, Twitter, YouTube from the source ASNs are found.
list_of_target_asns = [32934, 54115, 63293, 7224, 14618, 16509, 40027, 15169, 19448, 22859, 36039, 36384, 13414, \
                       35995, 54888, 36040, 36561, 43515]

# Iterate through all the ASNs in list of source ASNs
for asn in list_of_source_asns:
    # Start time to get measurements within a time window
    start_time = 1409130000
    # Stop time to get measurements within a time window
    stop_time = 1409140800

    # Specify filters to find probes in the US hosted in each ASN in list of source ASNs
    filters = {"asn": asn, "country_code": "US"}
    # Get probes in each ASN using ProbeRequest
    probes = ProbeRequest(**filters)
    # Iterate through the target ASNs
    for target in list_of_target_asns:
        # Specify the filters to find all the non-built-in traceroute measurements to a target
        mfilters = {"type": "traceroute", "target_asn": target}#, "start_time__gte": start_time, \
        # "stop_time__lte": stop_time}
        # Get the non-built-in traceroute measurements using MeasurementRequest
        msm_ids = MeasurementRequest(**mfilters)
        # Iterate through all the measurements found using MeasurementRequest
        for msm_id in msm_ids:
            # Iterate through each probe within an ASN
            for probe in probes:
                # Specify the filters to find the built-in measurements originating from the probe
                kwargs = {"msm_id": msm_id["id"], "probe_ids": probe["id"]}
                # Get results for each measurement ID and probe ID using AtlasResultsRequest
                is_success, results = AtlasResultsRequest(**kwargs).create()
                # Continue if successful
                if is_success:
                    # Iterate through all the results
                    for result in results:
                        print "Sending..."
                        print result
                        # Add the ASN to the result json to query the database DATABASE NAME
                        result["asn"] = asn
                        # Add the Target ASN to the result json to query the database DATABASE NAME
                        result["target_asn"] = target
                        # Store the result to the database DATABASE NAME/results
                        # results is the collection name within the database
                        db.results.insert_one(result)

print "Count:", db.results.count()
print "Fin."