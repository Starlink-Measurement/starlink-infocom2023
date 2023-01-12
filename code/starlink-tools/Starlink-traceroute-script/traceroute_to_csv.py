from pandas import DataFrame
from os import listdir
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import geopy.distance
from scr.tool import *
import argparse
import os

known_ip_list = []
known_ip_infos = []

def statisticalReport(data):
    protocol = []
    continent = []
    name = []
    num_of_test = []
    num_of_valid_trace = []
    s_d_ave_delay = []
    s_sat_ave_delay = []
    sat_d_ave_delay = []
    ave_hop = []
    city = []
    average_distance = []
    for domains in data:
        if domains.protocol == "udp":
            continue
        s_d_delay_sum = 0
        s_sat_delay_sum = 0
        hop_sum = 0
        valid_trace = 0
        destination_cities = []
        distance = []
        for trace_info in domains.traceInfos:
            if trace_info.status != "Trace found":
                continue
            valid_trace += 1
            for index in range(0, len(trace_info.delay)):
                if trace_info.domain_name[index].find("starlinkisp") != -1:
                    s_sat_delay_sum += float(trace_info.delay[index])
                    break
            s_d_delay_sum += float(trace_info.delay[-1])
            hop_sum += int(trace_info.hop_number[-1])
            index = arrayFind(known_ip_list,trace_info.ip[-1])
            if index == -1:
                loc_info = getIpLocInfo(trace_info.ip[-1])
                # Add the know information to the list
                known_ip_list.append(trace_info.ip[-1])
                known_ip_infos.append(loc_info)
            else:
                loc_info = known_ip_infos[index]
            if arrayFind(destination_cities, loc_info[2]) == -1:
                destination_cities.append(loc_info[2])
            distance.append(geopy.distance.distance((49.28, -123.12), (loc_info[0], loc_info[1])).km)
        protocol.append(domains.protocol)
        continent.append(domains.continent)
        name.append(domains.name)
        num_of_test.append(len(domains.traceInfos))
        num_of_valid_trace.append(valid_trace)
        city.append(','.join(destination_cities))
        if len(distance) == 0:
            average_distance.append(0)
        else:
            average_distance.append(sum(distance) / len(distance))
        if valid_trace == 0:
            s_d_ave_delay.append(0)
            s_sat_ave_delay.append(0)
            sat_d_ave_delay.append(0)
            ave_hop.append(0)
        else:
            s_d_ave_delay.append(s_d_delay_sum / valid_trace)
            s_sat_ave_delay.append(s_sat_delay_sum / valid_trace)
            sat_d_ave_delay.append(s_d_ave_delay[-1] - s_sat_ave_delay[-1])
            ave_hop.append(hop_sum / valid_trace)
    df = DataFrame({'Protocol': protocol, 'Continent': continent, 'Destination Name': name, \
        'Location': city, 'Physical distance': average_distance, 'Number of test': num_of_test,\
        'Number of successful traceroute': num_of_valid_trace, 'Ave arrive time (unit: ms)': s_d_ave_delay, \
        'Ave time between s-sat (unit: ms)': s_sat_ave_delay, \
        'Ave time between sat-d (unit: ms)': sat_d_ave_delay, 'Average hop needed': ave_hop})
    return df

def drawTracePath(data, outputPath):
    for domains in data:
        if domains.protocol == 'udp':
            continue
        lon_bound = [float('inf'), -float('inf')]
        lat_bound = [float('inf'), -float('inf')]
        unique_ip_pair = []
        unique_ipInfo_pair = []
        num_of_repeat_path = []
        unique_city = []
        unique_city_name = []
        for trace_info in domains.traceInfos:
            single_path_way = []
            for ip in trace_info.ip:
                curr_ip = ipInfos()
                curr_ip.ip = ip
                
                index = arrayFind(known_ip_list, ip)
                if(index == -1):
                    loc_info = getIpLocInfo(ip)
                    # Add the know information to the list
                    known_ip_list.append(ip)
                    known_ip_infos.append(loc_info)
                else:
                    loc_info = known_ip_infos[index]
                curr_ip.lat = loc_info[0]
                curr_ip.lon = loc_info[1]
                curr_ip.city = loc_info[2]        
                single_path_way.append(curr_ip)
             
            for i in range(0, len(single_path_way) - 1):
                ip_pair = (single_path_way[i].ip, single_path_way[i+1].ip)
                index = arrayFind(unique_ip_pair, ip_pair)
                if index == -1:
                    unique_ip_pair.append(ip_pair)
                    unique_ipInfo_pair.append((single_path_way[i], single_path_way[i+1]))
                    num_of_repeat_path.append(1)
                else:
                    num_of_repeat_path[i] += 1
            
            for i in single_path_way:
                if arrayFind(unique_city_name, i.city) == -1:
                    unique_city.append(i)
                    unique_city_name.append(i.city)
                if i.lon > lon_bound[1]:
                    lon_bound[1] = i.lon
                if i.lon < lon_bound[0]:
                    lon_bound[0] = i.lon
                if i.lat > lat_bound[1]:
                    lat_bound[1] = i.lat
                if i.lat < lat_bound[0]:
                    lat_bound[0] = i.lat
                
        # draw the diagram
        fig = plt.figure(figsize=(32, 24), edgecolor='w')
        width = lon_bound[1] - lon_bound[0]
        height = lat_bound[1] - lat_bound[0]
        map_lat = [lat_bound[0] - 15, lat_bound[1] + 15]
        map_lon = [lon_bound[0] - 15, lon_bound[1] + 15]
        m = Basemap(projection='cyl', resolution='c',
                llcrnrlat= map_lat[0], urcrnrlat= map_lat[1],
                llcrnrlon= map_lon[0], urcrnrlon= map_lon[1])
        draw_map(m)
        for i in range(0, len(unique_ipInfo_pair)):
            x, y = m([unique_ipInfo_pair[i][0].lon, unique_ipInfo_pair[i][1].lon], [unique_ipInfo_pair[i][0].lat, unique_ipInfo_pair[i][1].lat])
            plt.plot(x, y, 'o-', markersize=2, color=[0, 1, 0])
            midx = (unique_ipInfo_pair[i][0].lon + unique_ipInfo_pair[i][1].lon) / 2
            midy = (unique_ipInfo_pair[i][0].lat + unique_ipInfo_pair[i][1].lat) / 2
            x, y = m(midx, midy)
            plt.text(x, y, str(num_of_repeat_path[i]), verticalalignment='center')
        for i in range(0, len(unique_city)):
            x, y = m(unique_city[i].lon, unique_city[i].lat)
            if i % 2 == 1:
                plt.text(x, y, unique_city[i].city, horizontalalignment='left', verticalalignment='top', fontsize=12)
            else:
                plt.text(x, y, unique_city[i].city, horizontalalignment='right', verticalalignment='bottom', fontsize=12)

        if not os.path.exists(outputPath + """/graph"""):
            os.makedirs(outputPath + """/graph""")

        plt.savefig(outputPath + '/graph/{}-{}-{}-path-graph.png'.format(domains.protocol, domains.continent, domains.name))
        plt.close()

def main(args):
    data = []
    my_path = args.path
    for protocol in listdir(my_path):
        for continent in listdir("/".join([my_path, protocol])):
            for domains in listdir("/".join([my_path, protocol, continent])):
                newArea = targetDomain() 
                newArea.set(protocol, continent, domains)
                newArea.traceInfos = toTraceItems("/".join([my_path, protocol, continent, domains]))
                data.append(newArea)
    df = statisticalReport(data)
    if not os.path.exists(args.outputPath):
        os.makedirs(args.outputPath)
    df.to_csv(args.outputPath + "/traceroute_info.csv", index=False)
    if(args.pathGraph):
        drawTracePath(data, args.outputPath)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "A script to convert large-scale traceroute raw data to csv and path diagram.")
    parser.add_argument('-p', '--path', required=True, help='''The path to the target folder, target = ["Starlink_to_IPs", "Servers_to_Starlink"]''')
    parser.add_argument('-o', '--outputPath', default='.', help='The path to the output folder')
    parser.add_argument('--pathGraph', action='store_true', help='Also output the traceroute path graph')
    args = parser.parse_args()
    main(args)
