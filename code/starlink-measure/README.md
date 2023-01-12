# Starlink Measure

## Setup

Requirements:
- `iperf3` v3.6
- Terraform
- AWS-cli

Python packages:
- `json`

AWS-cli must be setup with `configure` and the desired regions must be enabled.

## Usage

Throughput measurements use `iperf3` to measure the per second TCP and UDP
download and upload throughput:

```
./run_world_iperf3.sh [-nh] [-d udp_download_bits] [-u udp_upload_bits] path/to/dest/folder
```

The throughput is measured at a set time interval switching sequentially
between all the specified regions.

The `-n` flag specifies not to create terraform instances just in case the
instances have already been created, for example, due to the ping measurements.

`-d` and `-u` are directly passed to `iperf3`, so values such as 10K is allowed
denoting 10 Kbits/sec as described in the `iperf3` documentation for the
`--bitrate` flag.

Ping is used to measure the per second latency in a continuous fashion. Ping is
sent to all the region instances simultaneously as they should not necessarily
interfere with each other much due to sending small packets.

```
./run_ping.sh [-nh] path/to/dest/folder
```

## Converting to CSV

Inside `plot_iperf` is a script `plot_dirs.sh` that will recursively convert
each iperf3 log file into individual `.csv` files. The columns are hardcoded,
so they would need to be changed if other entries are desired.
