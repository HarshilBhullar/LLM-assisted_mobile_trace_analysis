
#!/usr/bin/python3
# Filename: uplink_latency_analysis.py

"""
uplink_latency_analysis.py
Executes uplink latency analysis using the UplinkLatencyAnalyzer class
"""

import sys
import os
from mobile_insight.monitor import OfflineReplayer
from uplink_latency_analyzer import UplinkLatencyAnalyzer

def uplink_latency_analysis(log_file_path):
    """
    Perform uplink latency analysis on the given log file.

    :param log_file_path: Path to the log file containing LTE packet data.
    :return: Instance of UplinkLatencyAnalyzer after analysis.
    """
    # Initialize the data source
    source = OfflineReplayer()
    source.set_input_path(log_file_path)

    # Initialize the analyzer
    analyzer = UplinkLatencyAnalyzer()
    analyzer.set_source(source)

    # Start the analysis
    source.run()

    return analyzer

def calculate_and_print_statistics(analyzer):
    """
    Calculate and print uplink latency statistics based on the collected data.

    :param analyzer: Instance of UplinkLatencyAnalyzer containing analyzed data.
    """
    all_packets = analyzer.all_packets

    if not all_packets:
        print("No packet data available for analysis. Please check the log file.")
        return

    total_waiting_latency = 0
    total_tx_latency = 0
    total_retx_latency = 0

    for packet in all_packets:
        total_waiting_latency += packet['Waiting Latency']
        total_tx_latency += packet['Tx Latency']
        total_retx_latency += packet.get('Retx Latency', 0)

    total_latency = total_waiting_latency + total_tx_latency + total_retx_latency
    packet_count = len(all_packets)

    average_waiting_latency = total_waiting_latency / packet_count
    average_tx_latency = total_tx_latency / packet_count
    average_retx_latency = total_retx_latency / packet_count
    average_total_latency = total_latency / packet_count

    waiting_variance = sum((packet['Waiting Latency'] - average_waiting_latency) ** 2 for packet in all_packets) / packet_count
    tx_variance = sum((packet['Tx Latency'] - average_tx_latency) ** 2 for packet in all_packets) / packet_count
    retx_variance = sum((packet.get('Retx Latency', 0) - average_retx_latency) ** 2 for packet in all_packets) / packet_count
    total_variance = sum(((packet['Waiting Latency'] + packet['Tx Latency'] + packet.get('Retx Latency', 0)) - average_total_latency) ** 2 for packet in all_packets) / packet_count

    print(f"Total Latency: {total_latency}")
    print(f"Average Waiting Latency: {average_waiting_latency}")
    print(f"Average Transmission Latency: {average_tx_latency}")
    print(f"Average Retransmission Latency: {average_retx_latency}")
    print(f"Average Total Latency: {average_total_latency}")
    print(f"Latency Variance: {total_variance}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python uplink_latency_analysis.py <log_file_path>")
        sys.exit(1)

    log_file_path = sys.argv[1]

    if not os.path.isfile(log_file_path):
        print(f"Error: Log file {log_file_path} does not exist.")
        sys.exit(1)

    analyzer = uplink_latency_analysis(log_file_path)
    calculate_and_print_statistics(analyzer)
