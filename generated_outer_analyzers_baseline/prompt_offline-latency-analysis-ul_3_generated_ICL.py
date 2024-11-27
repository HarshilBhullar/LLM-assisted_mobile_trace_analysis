
#!/usr/bin/python3
# Filename: uplink_latency_outer_analyzer.py

"""
uplink_latency_outer_analyzer.py
An outer analyzer to utilize UplinkLatencyAnalyzer for uplink packet latency analysis
"""

import sys
from mobile_insight.monitor.offline_replayer import OfflineReplayer
from uplink_latency_analyzer import UplinkLatencyAnalyzer

def uplink_latency_analysis(log_path):
    """
    Initializes the OfflineReplayer and UplinkLatencyAnalyzer, then runs the analysis.

    :param log_path: The file path to the log file for analysis.
    :return: The UplinkLatencyAnalyzer object after analysis.
    """
    # Initialize OfflineReplayer as data source
    src = OfflineReplayer()
    src.set_input_path(log_path)

    # Create UplinkLatencyAnalyzer instance
    analyzer = UplinkLatencyAnalyzer()
    analyzer.set_source(src)

    # Run the source to perform analysis
    src.run()
    return analyzer

def calculate_metrics(analyzer):
    """
    Calculate and print latency metrics based on data from the analyzer.

    :param analyzer: The UplinkLatencyAnalyzer object after analysis.
    """
    # Retrieve all processed packet latencies
    packets = analyzer.all_packets

    if not packets:
        print("No relevant message types found in the provided log.")
        return

    # Initialize cumulative metrics
    total_waiting_latency = 0
    total_tx_latency = 0
    total_retx_latency = 0
    total_latency = 0

    # Calculate cumulative metrics
    for packet in packets:
        total_waiting_latency += packet['Waiting Latency']
        total_tx_latency += packet['Tx Latency']
        total_retx_latency += packet['Retx Latency']
        total_latency += packet['Waiting Latency'] + packet['Tx Latency'] + packet['Retx Latency']

    # Calculate averages
    num_packets = len(packets)
    avg_waiting_latency = total_waiting_latency / num_packets
    avg_tx_latency = total_tx_latency / num_packets
    avg_retx_latency = total_retx_latency / num_packets
    avg_total_latency = total_latency / num_packets
    avg_total_latency_excl_retx = (total_latency - total_retx_latency) / num_packets

    # Output results
    print(f"Average Waiting Latency: {avg_waiting_latency:.2f} ms")
    print(f"Average TX Latency: {avg_tx_latency:.2f} ms")
    print(f"Average Retx Latency: {avg_retx_latency:.2f} ms")
    print(f"Average Total Latency: {avg_total_latency:.2f} ms")
    print(f"Average Total Latency (Excluding Retx): {avg_total_latency_excl_retx:.2f} ms")

if __name__ == "__main__":
    log_file_path = './logs/offline_log_examples/20201115_181637_Xiaomi-Mi10_46000.mi2log'
    analyzer = uplink_latency_analysis(log_file_path)
    calculate_metrics(analyzer)
