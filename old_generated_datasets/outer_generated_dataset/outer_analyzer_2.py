
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
for latency in stats.all_packets:
    total_wait += latency['Waiting Latency']
    total_trans += latency['Tx Latency']
    total_retx += latency['Retx Latency']

total_latency = total_wait + total_trans + total_retx
n = len(stats.all_packets)

if n > 0:
    avg_latency = float(total_latency) / n
    avg_waiting_latency = float(total_wait) / n
    avg_tx_latency = float(total_trans) / n
    avg_retx_latency = float(total_retx) / n

    print("Average latency is:", avg_latency)
    print("Average waiting latency is:", avg_waiting_latency)
    print("Average tx latency is:", avg_tx_latency)
    print("Average retx latency is:", avg_retx_latency)

    # Additional output: calculate and print median latencies
    all_waiting_latencies = [latency['Waiting Latency'] for latency in stats.all_packets]
    all_tx_latencies = [latency['Tx Latency'] for latency in stats.all_packets]
    all_retx_latencies = [latency['Retx Latency'] for latency in stats.all_packets]

    median_waiting_latency = np.median(all_waiting_latencies)
    median_tx_latency = np.median(all_tx_latencies)
    median_retx_latency = np.median(all_retx_latencies)

    print("Median waiting latency is:", median_waiting_latency)
    print("Median tx latency is:", median_tx_latency)
    print("Median retx latency is:", median_retx_latency)

else:
    print("Certain message type(s) missing in the provided log.")
