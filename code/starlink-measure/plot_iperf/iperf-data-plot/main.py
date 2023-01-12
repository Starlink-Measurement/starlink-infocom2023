import jsonstream
import matplotlib.pyplot as plt
import sys
import argparse

import csv
import os

import traceback


def ema(data, window):
    if len(data) < window + 2:
        return None
    alpha = 2 / float(window + 1)
    ema = []
    for i in range(0, window):
        ema.append(None)
    ema.append(data[window])
    for i in range(window+1, len(data)):
        ema.append(ema[i-1] + alpha*(data[i]-ema[i-1]))
    return ema

COL_SEND_CWND = 'snd_cwnd'
COL_RTT = 'rtt'
COL_RTTVAR = 'rttvar'
COL_RETRANSMITS = 'retransmits'
COL_PARAID = 'parallel ID'
COL_BYTES = 'bytes'
COL_LOCAL_HOST = 'local_host'
COL_REMOTE_HOST = 'remote_host'

def chart(args, data, datawriter):
    # Setting the default values
    expected_bandwidth = 0
    ema_window = 9
    if args.protocol == 'udp':
        sum_string = 'sum'
    else:
        sum_string = 'sum_sent'
    if args.ema is not None:
        ema_window = int(args.ema)
    if args.expectedbw is not None:
        expected_bandwidth = int(args.expectedbw)

    debit = []
    intervals = data['intervals']

    datawriter.writerow(['timestamp', 'bits_per_second', COL_BYTES, COL_LOCAL_HOST, COL_REMOTE_HOST,
        'jitter_ms', 'lost_packets', 'packets', 'lost_percent', # UDP Headers
        COL_SEND_CWND, COL_RTT, COL_RTTVAR, COL_RETRANSMITS, COL_PARAID]) # TCP sending Headers

    start_timestamp = float(data['start']['timestamp']['timesecs']) # Starting timestamp in seconds
    local_host = data['start']['connected'][0][COL_LOCAL_HOST]
    remote_host = data['start']['connected'][0][COL_REMOTE_HOST]
    for i in intervals:
        sum_entry = i['sum']
        first_stream = i['streams'][0]
        timestamp = start_timestamp + float(sum_entry['start'])

        if COL_SEND_CWND in first_stream:
            for j, stream in enumerate(i['streams']):
                row = []
                row.append(timestamp)
                row.append(stream['bits_per_second'])
                row.append(stream[COL_BYTES])
                row.append(local_host)
                row.append(remote_host)
                row += [''] * 4 # UDP entries
                row.append(stream[COL_SEND_CWND])
                row.append(stream[COL_RTT])
                row.append(stream[COL_RTTVAR])
                row.append(stream[COL_RETRANSMITS])
                row.append(j)
                datawriter.writerow(row)

            continue # Skip rest as this is TCP sending

        row = []
        bps = sum_entry['bits_per_second']
        row.append(timestamp) # Timestamp
        row.append(bps)
        row.append(sum_entry[COL_BYTES])
        row.append(local_host)
        row.append(remote_host)
        if args.protocol == 'udp' and 'jitter_ms' in sum_entry:
            row.append(sum_entry['jitter_ms'])
            row.append(sum_entry['lost_packets'])
            row.append(sum_entry['packets'])
            row.append(sum_entry['lost_percent'])

        datawriter.writerow(row)
        #debit.append(bps)

    return # Skip plotting

    plt.plot(debit, label='Bandwitdh (per second)')

    plt.axhline(data['end'][sum_string]['bits_per_second'], color='r', label='Avg bandwidth')
    plt.axhline(expected_bandwidth * 1000000, color='g', label='Expected bandwidth')
    plt.plot(ema(debit, ema_window), label='Bandwidth {} period moving average'.format(ema_window))

    plt.title('{}, {}, {:.3}GB file'.format(data['start']['timestamp']['time'],
                                         data['start']['test_start']['protocol'],
                                         data['end'][sum_string]['bytes']/1000000000))
    plt.legend()
    if args.log:
        plt.yscale('log')
    else:
        plt.yscale('linear')
        plt.ylim(bottom=0)
    plt.ylabel('bit/s')
    plt.xlabel('time interval')
    plt.show()


def chart_objs(args, data):
    V_TEST_START = 'test_start'

    dest = 'csv_files'
    if args.output:
        dest = args.output
    os.makedirs(dest, exist_ok=True)
    filename = os.path.splitext(os.path.basename(args.input))[0]

    count = 0
    for d in data:
        out_filename = f"{filename}.{count}"
        start = d['start']
        if not V_TEST_START in start:
            print("Error in", args.input)
            if 'error' in d:
                print(' ', d['error'])
            else:
                print(' ', 'Unknown error')
            continue

        try:
            if d['start'][V_TEST_START]['protocol'] == 'UDP':
                args.protocol = 'udp'
                out_filename = f"{out_filename}.udp"
            else:
                args.protocol = 'tcp'
        except Exception:
            print("Error in", args.input)
            traceback.print_exc()
            continue

        dest_path = os.path.join(dest, f"{out_filename}.csv")
        with open(dest_path, 'w', newline='') as datafile:
            datawriter = csv.writer(datafile)
            chart(args, d, datawriter)

        count += 1


def be_verbose(args, data):
    print('Version 1.0 - Feb 2019')
    print('Command arguments are {}'.format(args))
    print('Start info : {}'.format(data['start']))
    print('End info : {}'.format(data['end']))


def main(argv):
    parser = argparse.ArgumentParser(description='Simple python iperf JSON data vizualiser. Use -J option with iperf to have a JSON output.')
    parser.add_argument('input', nargs='?', help='JSON output file from iperf')
    parser.add_argument('-o', '--output', nargs='?', help='Output folder')
    parser.add_argument('-a', '--ema', help='Exponential moving average used to smooth the bandwidth. Default at 9.', type=int)
    parser.add_argument('-e', '--expectedbw', help='Expected bandwidth to be plotted in Mb.')
    parser.add_argument('-v', '--verbose', help='Increase output verbosity', action='store_true')
    parser.add_argument('-l', '--log', help='Plot will be in logarithmic scale', action='store_true')
    args = parser.parse_args(argv)
    try:
        with open(args.input) as f:
            data = jsonstream.load(f)
            if args.verbose:
                be_verbose(args, data)
            chart_objs(args, data)
    except:
        print(args.input)
        raise


if __name__ == '__main__':
    main(sys.argv[1:])
