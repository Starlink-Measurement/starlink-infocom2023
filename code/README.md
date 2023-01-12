# Starlink Measurement Data Figure Generations

## Paper
Network Characteristics of LEO Satellite Constellations: 
A Starlink-Based Measurement from End Users

## Code and Data
The `.csv` files for `iperf3` data combines both sending and receiving logs
from both sides. If the parallel ID is filled, which demarcate individual
parallel flows, this entry is a *sending* or *uploading* entry.

The code is cloned from the following repositories (Tagged v1.0.0):

- [`starlink-measure`](https://github.com/Starlink-Measurement/starlink-measure.git) contains `iperf3` and `ping` measurement scripts and
automatically spins up AWS instances using Terraform.

- [`starlink-plot`](https://github.com/Starlink-Measurement/starlink-plot.git) is a series of Jupyter notebooks that was used to generate the
figures for the paper.

- [`starlink-tools`](https://github.com/Starlink-Measurement/starlink-tools.git) has the code for `traceroute` and streaming measurements.
