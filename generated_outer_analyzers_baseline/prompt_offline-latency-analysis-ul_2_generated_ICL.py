
#!/usr/bin/python3
# Filename: uplink_latency_analysis.py
"""
uplink_latency_analysis.py
A script to evaluate uplink packet waiting and processing latency using UplinkLatencyAnalyzer
"""

from mobile_insight.monitor import OfflineReplayer
from uplink_latency_analyzer import UplinkLatencyAnalyzer

def main():
    # Analysis Setup
    trace_file = "path/to/your/trace/file.mi2log"  # Set your trace log file path here
    replayer = OfflineReplayer()
    replayer.set_input_path(trace_file)

    uplink_analyzer = UplinkLatencyAnalyzer()
    uplink_analyzer.set_source(replayer)

    # Execute the data source to perform the analysis
    replayer.run()

    # Data Processing
    all_packets = uplink_analyzer.all_packets
    cum_err_block = uplink_analyzer.cum_err_block
    cum_block = uplink_analyzer.cum_block

    # Latency Calculation
    total_waiting_latency = sum(packet['Waiting Latency'] for packet in all_packets)
    total_tx_latency = sum(packet['Tx Latency'] for packet in all_packets)
    total_retx_latency = sum(packet['Retx Latency'] for packet in all_packets)

    total_latency = total_waiting_latency + total_tx_latency + total_retx_latency
    packet_count = len(all_packets)

    if packet_count > 0:
        avg_waiting_latency = total_waiting_latency / packet_count
        avg_tx_latency = total_tx_latency / packet_count
        avg_retx_latency = total_retx_latency / packet_count
        avg_latency = total_latency / packet_count
    else:
        avg_waiting_latency = 0
        avg_tx_latency = 0
        avg_retx_latency = 0
        avg_latency = 0

    # Output
    print(f"Average Waiting Latency: {avg_waiting_latency:.2f} ms")
    print(f"Average Transmission Latency: {avg_tx_latency:.2f} ms")
    print(f"Average Retransmission Latency: {avg_retx_latency:.2f} ms")
    print(f"Average Total Latency: {avg_latency:.2f} ms")

    # Weighted Average Latency Calculation
    waiting_weight = 0.4
    tx_weight = 0.4
    retx_weight = 0.2
    weighted_avg_latency = (waiting_weight * avg_waiting_latency +
                            tx_weight * avg_tx_latency +
                            retx_weight * avg_retx_latency)
    print(f"Weighted Average Latency: {weighted_avg_latency:.2f} ms")

    # Feedback on missing message types
    if cum_block[0] == 0 or cum_err_block[0] == 0:
        print("Warning: Some expected message types are missing in the log, which may affect analysis results.")

if __name__ == "__main__":
    main()
