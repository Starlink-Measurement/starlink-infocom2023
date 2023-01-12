## Scraper Execution:

`python scraper.py -n filename.csv -t 60 -s 0`

## Input argument:

-n      the file name for the output csv file.

-t      record time period (in seconds).

-s      shutdown after task finish (1/0)

# Note:

After execute the script, the scraper will open the chrome and wait for user to open the stats of nerd windows and set the appropriate resolution. After user did that, input anything in the terminal to start recording.

## CSV to diagram Execution:

`python3 csv_to_diagram.py -p Streaming_data.csv -o "./" --prefix "test-"`

## Input argument:

-h      to show help information

