import argparse
import os
import pandas as pd
from pathlib import Path

def main(args):
  my_path = args.path
  for protocol in os.listdir(my_path):
    for continent in os.listdir("/".join([my_path, protocol])):
      for domains in os.listdir("/".join([my_path, protocol, continent])):
        start_id = 0
        txt_paths = sorted(Path("/".join([my_path, protocol, continent, domains])).iterdir(), key = os.path.getmtime)
        id = []
        timestamp = []
        trace_string = []
        for path in txt_paths:
          current_txt = open(path, 'r')
          create_time = int(os.path.getmtime(path))
          for line in current_txt.readlines():
            id.append(start_id)
            timestamp.append(create_time)
            trace_string.append(line.replace('\n', ''))
          start_id += 1

        csv_pd = pd.DataFrame({'id': id, 'timestamp': timestamp, 'trace_string':trace_string})
        if not os.path.exists("/".join([args.outputPath, protocol, continent])):
          os.makedirs("/".join([args.outputPath, protocol, continent]))
        csv_pd.to_csv("/".join([args.outputPath, protocol, continent]) + "/" + domains + ".csv", index=False)
          
          

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description = "A script to convert old txt data format to csv data format.")
  parser.add_argument('-p', '--path', required=True, help='''The path to the target folder, target = ["Starlink_to_IPs", "Servers_to_Starlink"]''')
  parser.add_argument('-o', '--outputPath', default='Starlink_to_IPs_csv', help='The path to the output folder')
  args = parser.parse_args()
  main(args)