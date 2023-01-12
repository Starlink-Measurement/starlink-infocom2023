import pandas as pd
import matplotlib.pyplot as plt
import argparse
import pytz
from matplotlib.dates import DateFormatter

# Input argvs:  1 - input csv file name
#               2 - diagram output path (leave umpty will not save the image)

def main(args):
    df = pd.read_csv(args.path)

    df["timestamp"] = df["timestamp"].apply(lambda x: pd.to_datetime(x, unit = 's'))
    df["connection speed"] = df["connection speed"].apply(lambda x: int(''.join(c for c in x if c.isdigit())))
    df["network activity"] = df["network activity"].apply(lambda x: int(''.join(c for c in x if c.isdigit())))
    df["buffer health"] = df["buffer health"].apply(lambda x: float(''.join(c for c in x if c.isdigit() or c == '.')))

    outage_log = []
    if args.outageFile1 != None:
        df_log = pd.read_csv(args.outageFile1)    
        for cols in df_log['timestamp']:
            outage_log.append(cols)
        outage_log = pd.to_datetime(outage_log)

    hh_mm = DateFormatter('%H:%M:%S', tz = pytz.timezone('America/Vancouver'))

    # satellite_handover = pd.read_csv("/mnt/d/Study/master project/starlink/github/starlink-satellite-analyze/satellite_handover.csv")
    # timestamp_list = pd.to_datetime(satellite_handover['timestamp'][(satellite_handover['timestamp'] > 1654066984.3691401) \
    #      & (satellite_handover['timestamp'] < 1654092183.87344)].tolist(), unit='s')

    # The following draw the comparsion diagram for two CSV file on the buffer health
    if args.path2 != None:
        df2 = pd.read_csv(args.path2)

        df2["timestamp"] = df2["timestamp"].apply(lambda x: pd.to_datetime(x, unit = 's'))
        df2["connection speed"] = df2["connection speed"].apply(lambda x: int(''.join(c for c in x if c.isdigit())))
        df2["network activity"] = df2["network activity"].apply(lambda x: int(''.join(c for c in x if c.isdigit())))
        df2["buffer health"] = df2["buffer health"].apply(lambda x: float(''.join(c for c in x if c.isdigit() or c == '.')))

        # Only take the overlapped time period
        lower_bound = max(df['timestamp'][0], df2['timestamp'][0])
        upper_bound = min(df.iloc[-1]['timestamp'], df2.iloc[-1]['timestamp'])
        df = df[(df['timestamp'] > lower_bound) & (df['timestamp'] < upper_bound)]
        df2 = df2[(df2['timestamp'] > lower_bound) & (df2['timestamp'] < upper_bound)]

        outage_log2 = []
        if args.outageFile2 != None:
            df_log = pd.read_csv(args.outageFile2)    
            for cols in df_log['timestamp']:
                outage_log2.append(cols)
            outage_log2 = pd.to_datetime(outage_log2)

        fig, axis = plt.subplots(nrows=2, ncols=1)

        ax1 = df.plot(x = 'timestamp', y = 'buffer health', kind = 'scatter', figsize=(10,6), ax=axis[0], xlabel="", ylabel="")
        for ots in outage_log:
            # Convert the ots into UTC time, since it is localized time (e.g., Vancouver)
            utc = ots.tz_convert(None)
            if (utc > lower_bound) and (utc < upper_bound):
                ax1.axvline(x = ots, linestyle = '-', color = 'r')
        plt.autoscale(enable=True, axis='both', tight=None)
        ax1.xaxis.set_major_formatter(hh_mm)

        ax2 = df2.plot(x = 'timestamp', y = 'buffer health', kind = 'scatter', figsize=(10,6), ax=axis[1], xlabel="", ylabel="")
        for ots in outage_log2:
            # Convert the ots into UTC time, since it is localized time (e.g., Vancouver)
            utc = ots.tz_convert(None)
            if utc > lower_bound and utc < upper_bound:
                ax2.axvline(x = ots, linestyle = '-', color = 'r')
        plt.autoscale(enable=True, axis='both', tight=None)
        ax2.xaxis.set_major_formatter(hh_mm)

        fig.supxlabel('Timestamp')
        fig.supylabel('Buffer Health (in seconds)')

        if args.outputPath != None:
            plt.savefig(args.outputPath + args.prefix + "buffer health.png", bbox_inches='tight')

    # The following draw the three diagram for the single CSV file
    else:
        fig1 = plt.figure(0)
        ax1 = df.plot(x = 'timestamp', y = 'buffer health', xlabel = 'timestamp', 
                    ylabel = 'buffer health (second)', kind = 'scatter', figsize=(10,6))
        for ots in outage_log:
            plt.axvline(x = ots, linestyle = '-', color = 'r')
        plt.autoscale(enable=True, axis='both', tight=None)
        plt.xticks(rotation=60)
        ax1.xaxis.set_major_formatter(hh_mm)
        if args.outputPath != None:
            plt.savefig(args.outputPath + args.prefix + "buffer health.png", bbox_inches='tight')

        fig2 = plt.figure(1)
        ax2 = df.plot(x = 'timestamp', y = 'network activity', xlabel = 'time stamp', 
                    ylabel = 'network activity (KB)', kind = 'scatter', figsize=(6,6))
        for ots in outage_log:
            plt.axvline(x = ots, linestyle = '-', color = 'r')
        plt.autoscale(enable=True, axis='both', tight=None)
        plt.xticks(rotation=60)
        ax2.xaxis.set_major_formatter(hh_mm)
        if args.outputPath != None:
            plt.savefig(args.outputPath + args.prefix + "network activity.png")

        fig3 = plt.figure(2)
        ax3 = df.plot(x = 'timestamp', y = 'connection speed', xlabel = 'time stamp',
                    ylabel = 'connection speed (Kbps)', kind = 'scatter', figsize=(6,6))
        for ots in outage_log:
            plt.axvline(x = ots, linestyle = '-', color = 'r')
        plt.autoscale(enable=True, axis='both', tight=None)
        plt.xticks(rotation=60)
        ax3.xaxis.set_major_formatter(hh_mm)
        if args.outputPath != None:
            plt.savefig(args.outputPath + args.prefix + "connection speed.png")

    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "This script will convert the Youtube scraper output file to a diagram.\n" + \
                                     "Without the '-p2' flag, the script will draw the buffer health, network activity and connection speed diagram for the single CSV file." + \
                                     "With the '-p2' flag, the script will draw the comparsion buffer health diagram between two CSV file.")
    parser.add_argument('-p', '--path', help='The path to the CSV input file', required=True)
    parser.add_argument('-p2', '--path2', help='The path to the second CSV input file (Optional)')
    parser.add_argument('--outageFile1', help='The path to the first outage log file (Optional)')
    parser.add_argument('--outageFile2', help='The path to the second outage log file (Optional)')
    parser.add_argument('-o', '--outputPath', help='The path of the output diagram. The diagram will not be saved if left empty.')
    parser.add_argument('--prefix', help="The prefix of all diagram name (Optional).", default="")
    args = parser.parse_args()
    main(args)
