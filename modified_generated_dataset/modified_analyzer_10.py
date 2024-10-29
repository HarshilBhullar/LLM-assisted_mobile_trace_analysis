#!/usr/bin/python

import os
import sys
import shutil
import traceback

import matplotlib.pyplot as plt
import numpy as np

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import UplinkLatencyAnalyzer


def uplink_latency_analysis():
    src = OfflineReplayer()
    src.set_input_path(sys.argv[1])

    analyzer = UplinkLatencyAnalyzer()
    analyzer.set_source(src)

    src.run()

    return analyzer


stats = uplink_latency_analysis()

total_latency = 0
total_wait = 0
total_trans = 0
total_retx = 0

total_retx = 8 * stats.cum_err_block[0]
latencies = []

for latency in stats.all_packets:
    total_wait += latency['Waiting Latency']
    total_trans += latency['Tx Latency']
    total_retx += latency['Retx Latency']
    packet_latency = latency['Waiting Latency'] + latency['Tx Latency'] + latency['Retx Latency']
    latencies.append(packet_latency)

total_latency = total_wait + total_trans + total_retx
n = len(stats.all_packets)

if n > 0:
    average_latency = float(total_latency) / n
    print("Average latency is:", average_latency)
    print("Average waiting latency is:", float(total_wait) / n)
    print("Average tx latency is:", float(total_trans) / n)
    print("Average retx latency is:", float(total_retx) / n)

    # Calculate jitter as the variance of the latencies
    jitter = np.var(latencies)
    print("Jitter (latency variance) is:", jitter)
else:
    print("Certain message type(s) missing in the provided log.")

# ### Key Modifications:
# 1. **Jitter Calculation**: Added calculation of jitter as the variance of the packet latencies using NumPy's `np.var` function. This provides insight into the consistency of the latency times.
# 2. **latencies List**: Introduced a list to store individual packet latencies for the variance calculation.

# These changes maintain compatibility with the existing codebase structure while introducing a new metric for analysis.