import urllib2
from ipwhois import IPWhois
import json
from GetMeasurements import Get
import geocoder
from geoip import geolite2
from SaveMeasurements import Save

Final = {}
prev_name_net=0
description = ""
dest_name=""
inter_network_name=""

def perfomance_d(start, end, asn):
    Fin=[]
    Final = {}
    prev_name_net = 0
    description = ""
    g = []
    r = {}
    fin = []
    Net = []
    Route_for_network = {}
    c_dict = {}
    c_dict_final = {}
    v_dict = {}
    chart_dict = {}

    measurements = Get()
    current_measurements = measurements.getMeasurements(asn, start, end)

    for res in current_measurements:
        RTT_med = 0
        isp_RTT = 0
        list = []
        print "Measurement"
        new_count = 0
        counter = 0
        prev_asn_name = " "

        Total_h = len(res['result'])

        if res['result'][Total_h - 1]['hop'] != 255:
            for i in range(0, Total_h):

                try:
                    hop_ip = res['result'][i]['result'][0]['from']
                    # print "Hop" ,hop
                    obj = IPWhois(str(hop_ip))                                       #find the asn number using the hop on each ip
                    results = obj.lookup_whois()
                    now_asn = results['asn']

                    # print results
                    match = geolite2.lookup(str(hop_ip))
                    z = match.location                                              # find the location of each hop
                    print z
                    if z[0] == 38.0 and z[1] == -97.0:
                        g = geocoder.arcgis(str(results['nets'][0]['city']))
                        print((g.latitude, g.longitude))
                        z = (g.latitude, g.longitude)
                    new_count += 1
                    url = "http://stat.ripe.net/data/as-overview/data.json?resource=AS" + str(results['asn'])
                    url = url.strip()
                    data2 = json.load(urllib2.urlopen(url))
                    response_data = data2["data"]
                    network = response_data["holder"].split()
                    inter_network_name = network[0]                                   # find asn name
                    if j == 0:
                        prev_asn_name = inter_network_name
                        j = 1
                    else:
                        if prev_asn_name != inter_network_name and counter < 1 and now_asn != "NA" and \
                                        prev_result['nets'][0]['description'] != results['nets'][0]['description']:
                            hop_no = i - 1
                            counter = 1
                            name = prev_asn_name
                            isp_RTT = RTT_med                                                                   # find the edge
                            description = prev_result['nets'][0]['description']
                            latitude = z[0]
                            longitude = z[1]

                            print "-----------------------------------------------EDGE--------------------------------------------------------"

                    print "Hop ip", i + 1, "    ", hop_ip, "  ", inter_network_name, "  ", now_asn, ",", z, " ",results['nets'][0]['description']

                    rtt = []
                    pack_size = res['result'][i]['result'][0]['size']
                    rtt.append(res['result'][i]['result'][0]['rtt'])
                    rtt.append(res['result'][i]['result'][1]['rtt'])
                    rtt.append(res['result'][i]['result'][2]['rtt'])                                          # find RTT for all three packets
                    RTT_med = sorted(rtt)[len(rtt) // 2]                                                     # find the RTT median
                    print "RTT_med:", RTT_med
                    print "isp_RTT:", isp_RTT
                    dest_name=inter_network_name
                    d1 = {"Name": inter_network_name, "lat": z[0], "lng": z[1], "RTT": RTT_med}
                    list.append(d1)
                    prev_asn = now_asn
                    prev_result = results

                except Exception as e:
                    print e
                    inter_network_name = "Unknown"

        d2 = {"traceroute": list, "timestamp": res['timestamp'], "Destination": dest_name,                   # create dict
              "isp": description, "isp_rtt": isp_RTT,
              "Final_rtt": RTT_med}  # put in the dict "Traceroute": list,
        # print description
        if isp_RTT!=0 and RTT_med!=0:

            line_1 = ['Comcast']
            for l in range(len(line_1)):
                result_2 = bool(line_1[l] in description)
                if result_2 == True:
                    d2["isp"] = "Comcast"
                    random = 0
                    if d2['Destination'] in c_dict:
                        c_dict[d2['Destination']][0].append((isp_RTT, RTT_med))
                        c_dict[d2['Destination']].append(d2["traceroute"])
                    else:
                        c_dict[d2['Destination']] = [[(isp_RTT, RTT_med)]]
                        c_dict[d2['Destination']].append(d2["traceroute"])
            line_1 = ['Verizon', 'UUNET', 'ANS Communications']
            for l in range(len(line_1)):
                result_2 = bool(line_1[l] in description)
                if result_2 == True:
                    d2["isp"] = "Verizon"
                    random = 0
                    if d2['Destination'] in v_dict:
                        v_dict[d2['Destination']][0].append((isp_RTT, RTT_med))
                        v_dict[d2['Destination']].append(d2["traceroute"])
                    else:
                        v_dict[d2['Destination']] = [[(isp_RTT, RTT_med)]]
                        v_dict[d2['Destination']].append(d2["traceroute"])

            line_1 = ['Time Warner Cable', 'ROADRUNNER', 'Charter', "BRIGHT HOUSE NETWORKS"]
            for l in range(len(line_1)):
                result_2 = bool(line_1[l] in description)
                if result_2 == True:
                    d2["isp"] = "Charter"
                    random = 0
                    if d2['Destination'] in chart_dict:
                        chart_dict[d2['Destination']][0].append((isp_RTT, RTT_med))
                        chart_dict[d2['Destination']].append(d2["traceroute"])

                    else:
                        chart_dict[d2['Destination']] = [[(isp_RTT, RTT_med)]]
                        chart_dict[d2['Destination']].append(d2["traceroute"])


    dictionary = [chart_dict, c_dict, v_dict]
    name_net = ""
    for k in dictionary:
        a=[]
        Aggregate_Route = []
        lis1 = []
        lis2 = []

        for d in k:
            try:
                if lis1 != [] or lis1 != 0 or lis2 != [] or lis2 != 0:
                    for i in k[d][0]:
                        if i != (0, 0):
                            lis1.append(i[0])
                            lis2.append(i[1])
                    l = filter(lambda a: a != 0, lis1)
                    l2 = filter(lambda a: a != 0, lis2)
                    if l != [] and l2 != [] and l != 0 and l2 != 0:
                        r = reduce(lambda x, y: x + y, l) / len(l)
                        r2 = reduce(lambda x, y: x + y, l2) / len(l2)

                        lat_prb = k[d][1][0]['lat']
                        Lon_prb = k[d][1][0]['lng']
                        name_prb = k[d][1][0]['Name']
                        Len = len(k[d][1])

                        lat_fin = k[d][1][Len - 1]['lat']
                        lon_fin = k[d][1][Len - 1]['lng']
                        name_fin = k[d][1][Len - 1]['Name']
                        k[d] = filter(lambda a: a != 0, k[d])
                        Aggregate_Route = {"Destination": d, "ISP_RTT": r, "Traceroutes": k[d], "Final_RTT": r2,
                                           "Aggregate_Route": [{"Name": name_prb, "lat": lat_prb, "lng": Lon_prb},
                                                               {"Name": name_fin, "lat": lat_fin, "lng": lon_fin}]}
                a.append(Aggregate_Route)

            except:
                "Error"

            if k == chart_dict:
                name_net = "Charter"
            elif k == c_dict:
                name_net = "Comcast"

            elif k == v_dict:
                name_net = "Verizon"
        if a!=[]:
            Route_for_network = {"Name": name_net, "Aggregate_Routes": a}
            Net.append(Route_for_network)
        Fin = filter(None, Net)
    if Fin != []:
        # final_network_dictionary = switchNames(network_dictionary)
        prev_name_net = name_net
        Final_1 = {"Networks": Fin}
        to_save = Save()
        to_save.saveMeasurements(Final_1)
        measurements.closeConnection()
        to_save.closeConnection()
        print "Final", Final_1


# Jan 1 2017 = 1483228800
# Jan 10 2017 = 1484006400
def main():
    perfomance_d(1483228800, 1484006400, 20115)

if __name__ == '__main__':
    main()
