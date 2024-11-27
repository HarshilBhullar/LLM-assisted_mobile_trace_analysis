
#!/usr/bin/python
# Filename: uplink_latency_analysis.py

"""
Offline analysis for uplink latency using UplinkLatencyAnalyzer
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import UplinkLatencyAnalyzer

import numpy as np

def uplink_latency_analysis():
    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")
    
    uplink_analyzer = UplinkLatencyAnalyzer()
    uplink_analyzer.set_source(src)

    # Start the monitoring
    src.run()

    return uplink_analyzer

if __name__ == "__main__":
    stats = uplink_latency_analysis()
    
    # Calculate total and average latencies
    total_latency = 0
    total_wait = 0
    total_trans = 0
    total_retx = 0

    for latency in stats.all_packets:
        total_wait += latency['Waiting Latency']
        total_trans += latency['Tx Latency']
        total_retx += latency['Retx Latency']

    total_latency = total_wait + total_trans + total_retx
    n = len(stats.all_packets)

    if n > 0:
        avg_wait = total_wait / n
        avg_trans = total_trans / n
        avg_retx = total_retx / n
        avg_latency = total_latency / n
        
        latency_variances = [(latency['Waiting Latency'] + latency['Tx Latency'] + latency['Retx Latency'] - avg_latency) ** 2 for latency in stats.all_packets]
        variance = sum(latency_variances) / n
    else:
        avg_wait = avg_trans = avg_retx = avg_latency = variance = 0.0

    print(f"Total Latency: {total_latency:.2f}")
    print(f"Average Waiting Latency: {avg_wait:.2f}")
    print(f"Average Transmission Latency: {avg_trans:.2f}")
    print(f"Average Retransmission Latency: {avg_retx:.2f}")
    print(f"Average Total Latency: {avg_latency:.2f}")
    print(f"Latency Variance: {variance:.2f}")
