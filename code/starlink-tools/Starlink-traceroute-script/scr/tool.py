from re import I
from urllib.request import urlopen
from itertools import chain
import numpy as np
import json
import pandas as pd

class traceItem:
    def __init__(self) -> None:
        self.hop_number = []
        self.domain_name = []
        self.ip = []
        self.delay = []
        self.status = ""
    def add(self, hop_number, domain_name, ip, delay):
        self.hop_number.append(hop_number)
        self.domain_name.append(domain_name)
        self.ip.append(ip)
        self.delay.append(delay)
    def show(self):
        print('[hop number, domain name, ip, delay, status]:')
        for i in range(0, len(self.domain_name)):
            print('[{}, {}, {}, {}]'.format(self.hop_number[i], self.domain_name[i], self.ip[i], self.delay[i]))
        print('Trace status: {}'.format(self.status))
    def arriveDelay(self):
        return self.delay[-1]

class targetDomain:
    def __init__(self) -> None:
        self.protocol = ""
        self.continent = ""
        self.name = ""
        self.city_name = ""
        self.traceInfos = []        # A array of class traceItem
    def set(self, protocol, continent, target_domian):
        self.protocol = protocol
        self.continent = continent
        self.name = target_domian
    def show(self):
        print('Protocol: {}\nContient: {}\nTarget domain: {}\nNumber of tests: {}\nThe detais as follow:\n'\
            .format(self.protocol, self.continent, self.name, len(self.traceInfos)))
        for i in range(0, len(self.traceInfos)):
            print('***The {}th test:***'.format(i+1))
            self.traceInfos[i].show()

class ipInfos:
    def __init__(self) -> None:
        self.ip = ""
        self.lon = 0
        self.lat = 0
        self.city = ""
    def show(self):
        print('[Ip: {}, lon: {}, lat: {}, city: {}]'.format(self.ip, self.lon, self.lat, self.city))

def getIpLocInfo(ip):
    url = 'https://ipinfo.io/' + ip + '/json'
    res = urlopen(url)
    result = json.load(res)
    if "bogon" in result:       # private ip
        if result['bogon']:
            return 49.28, -123.12, 'Vancouver'
    city = result['city']
    loc = result['loc'].split(',')
    if city == None:
        city = "Unknown"
    return float(loc[0]), float(loc[1]), city

def arrayFind(array, item):
    try:
        index = array.index(item)
    except:
        index = -1
    return index

def toTraceItems(path):
    trace_infos = []
    trace_pd = pd.read_csv(path)
    current_id = trace_pd['id'][0]
    i = 0
    while i < trace_pd.shape[0]:
        current_item = traceItem()
        trace_status = "Trace found"
        while i < trace_pd.shape[0]:
            if current_id != trace_pd['id'][i]:
                break
            # Three case to skip the current line
            # 1. The current prob is lost (* * *)
            # 2. len(line) < 10 here can prevent the traceroute process being
            # interrupted, so it didn't reach 30
            # 3. This is the first line of traceroute result (e.g., treaceroute to ...)
            line = trace_pd['trace_string'][i]
            item_list = line.split()
            if(line.find('* * *') != -1 or len(line) < 10 or \
                line.find('traceroute to') != -1):
                # This traceroute lost
                if(item_list[0] == '30'):
                    trace_status = "Trace lost"
                # This hop lost, go to the next hop
                i += 1
                continue
            hop_number = item_list[0]
            ave_delay = 0
            num_of_arrived_probs = 0
            for item_index in range(0, len(item_list)):
                # This is a RTT number
                if item_list[item_index].find("ms") != -1 and \
                    len(item_list[item_index]) == 2:
                    ave_delay += float(item_list[item_index - 1])
                    num_of_arrived_probs += 1
                # This is a ip address
                elif item_list[item_index].find('(') != -1 and \
                    item_list[item_index].find(')') != -1:
                    ip = item_list[item_index][1:-1]
                    domain_name = item_list[item_index - 1]
            ave_delay /= num_of_arrived_probs
            current_item.add(hop_number, domain_name, ip, ave_delay)
            i += 1
        if len(current_item.delay) == 0:
            trace_status = "Trace failed"
        current_item.status = trace_status
        trace_infos.append(current_item)
        # renew the id if i still in the range
        if i < trace_pd.shape[0]:
            current_id = trace_pd['id'][i]

    return trace_infos

def draw_map(m, scale=0.2):
    # draw a shaded-relief image
    # m.shadedrelief(scale=scale)
    m.fillcontinents()
    
    # lats and longs are returned as a dictionary
    lats = m.drawparallels(np.linspace(-90, 90, 13))
    lons = m.drawmeridians(np.linspace(-180, 180, 13))

    # keys contain the plt.Line2D instances
    lat_lines = chain(*(tup[1][0] for tup in lats.items()))
    lon_lines = chain(*(tup[1][0] for tup in lons.items()))
    all_lines = chain(lat_lines, lon_lines)
    
    # cycle through these lines and set the desired style
    for line in all_lines:
        line.set(linestyle='-', alpha=0.3, color='w')
