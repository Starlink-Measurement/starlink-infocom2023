# iperf-data-plot  
Simple python iperf JSON data vizualiser. Final plot of the data will include a moving average, the expected bandwidth you entered and the average measured bandwidth.  

### Requirements  
It works on Python3, with iperf 3.1.3. I have not tested it with any other version.  
Required python3 package : *matplotlib*

### Usage
```
usage: main.py [-h] [-a EMA] [-e EXPECTEDBW] [-v] [input]  

Simple python iperf JSON data vizualiser. Use -J option with iperf to have a JSON output.

positional arguments:  
    input JSON output file from iperf

optional arguments:  
    -h, --help                       Show this help message and exit
    -a EMA, --ema EMA     Exponential moving average used to smooth the bandwidth. Default at 60.
    -e N, --expectedbw N  Expected bandwidth to be plotted in Mb.
    -v, --verbose                 Increase output verbosity
    -l, --log                           Plot will be in logarithmic scale
```

### Known bug
If ema size is bigger than the number of measurement points, then it crashes.