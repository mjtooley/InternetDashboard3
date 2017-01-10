"""
This file is to get the non-built-in traceroute results originating from ISP ASNs from RIPE Atlas servers and store
those results in MongoDB.
"""

from pymongo import MongoClient
from ripe.atlas.cousteau import MeasurementRequest, AtlasResultsRequest, ProbeRequest

# Connect to the database using pymongo. No arguments to MongoClient() connects to the localhost at port 27017.
# Else, connect to the database at the specified IP address and port number
client = MongoClient()#"172.25.11.132", 27017)
# Specify the database name at that IP address. (Database Name = AllASNsTWCOutage)
db = client.AllASNsTWCOutage

# Create a list of ASNs from which the measurement originates
list_of_source_asns = [7922, 22773, 20115, 6128, 30036, 10796, 11351, 11426, 11427, 12271, 20001, 19108, 7018, 20057, \
                       701, 22394, 209, 22561, 26868, 6939, 109, 3943, 174, 292, 1280, 2914, 3549, 5650, 4323, 6621, \
                       7065, 7155, 11492, 12276, 16591, 32440, 33363, 33445, 36692, 394536, 40285]
# target_asns is used to find results from the database Internet_Dashboard/interconnects, if measurements going to
# Google, Facebook, Amazon, Netflix, Twitter, YouTube from the source ASNs are found.
target_asn = None

# Start time to get measurements within a time window
start_time = 1409130000
# Stop time to get measurements within a time window
stop_time = 1409140800

# Specify the filters to find all the non-built-in traceroute measurements within a time window
filters = {"type": "traceroute", "start_time__gte": start_time, "stop_time__lte": stop_time}
# Get the non-built-in traceroute measurements within a time window using MeasurementRequest
msms = MeasurementRequest(**filters)

# Iterate through all the measurements found using MeasurementRequest
for msm in msms:
    # Specify the filters to find the measurements using measurement ID
    kwargs = {"msm_id": msm["id"]}
    # Get results for each measurement ID using AtlasResultsRequest
    is_success, results = AtlasResultsRequest(**kwargs).create()
    # Continue if successful
    if is_success:
        # Iterate through all the results
        for result in results:
            # Iterate through all the ASNs in list of source ASNs
            for asn in list_of_source_asns:
                # Specify filters to find probes in the US hosted in each ASN in list of source ASNs
                filters = {"asn": asn, "country_code": "US"}
                # Get probes in each ASN using ProbeRequest
                probes = ProbeRequest(**filters)
                # Iterate through each probe within an ASN
                for probe in probes:
                    # If the result originated from a probe in one of the source ASNs, store it to the database
                    if probe["id"] == result["prb_id"]:
                        print "Sending..."
                        # Add the ASN to the result json to query the database DATABASE NAME
                        result["asn"] = asn
                        print result
                        # Add the Target ASN to the result json to query the database DATABASE NAME
                        result["target_asn"] = target_asn
                        # Store the result to the database DATABASE NAME/results
                        # results is the collection name within the database
                        db.results.insert_one(result)
                        print result["msm_id"], result["prb_id"]
print "Count:", db.results.count()
print "Fin."