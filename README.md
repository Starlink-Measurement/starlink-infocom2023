# Starlink Measurement Data Figure Generations

## Paper
Network Characteristics of LEO Satellite Constellations: 
A Starlink-Based Measurement from End Users

## Code and Data
Run the following to acquire all the submodules:
```
git submodule update --init --recursive
```

The `.csv` files not in folders are mostly a combined export of their respective
data type, i.e., `2022-06-05_end_all_starlink_iperf3.csv` is all the `iperf3` data
for the typical Starlink dish in Burnaby and the terrestrial network.

The `.csv` files for `iperf3` data combines both sending and receiving logs
from both sides. If the parallel ID column has an entry (One of \[0,3\]), 
which demarcate individual parallel flows, this entry is a *sending* or *uploading* entry.

The code is cloned from the following repositories (Tagged v1.0.0):

- [`starlink-measure`](https://github.com/Starlink-Measurement/starlink-measure.git) contains `iperf3` and `ping` measurement scripts and
automatically spins up AWS instances using Terraform.

- [`starlink-plot`](https://github.com/Starlink-Measurement/starlink-plot.git) is a series of Jupyter notebooks that was used to generate the
figures for the paper.

- [`starlink-tools`](https://github.com/Starlink-Measurement/starlink-tools.git) has the code for `traceroute` and streaming measurements.
