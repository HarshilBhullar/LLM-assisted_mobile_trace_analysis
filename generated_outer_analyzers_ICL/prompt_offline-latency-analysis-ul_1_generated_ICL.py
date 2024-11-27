
#!/usr/bin/python3
# Filename: uplink-latency-analysis.py
import os
import sys

"""
Uplink latency analysis by replaying logs
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, UplinkLatencyAnalyzer

def uplink_latency_analysis():
    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")

    src.enable_log("LTE_PHY_PUSCH_Tx_Report")
    src.enable_log("LTE_MAC_UL_Buffer_Status_Internal")

    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./uplink_latency_analysis.txt")
    logger.set_source(src)

    uplink_latency_analyzer = UplinkLatencyAnalyzer()
    uplink_latency_analyzer.set_source(src)

    # Start the monitoring
    src.run()

    return uplink_latency_analyzer

if __name__ == "__main__":
    analyzer = uplink_latency_analysis()

    # Compute latency statistics
    if analyzer.all_packets:
        total_waiting_latency = sum([pkt['Waiting Latency'] for pkt in analyzer.all_packets])
        total_tx_latency = sum([pkt['Tx Latency'] for pkt in analyzer.all_packets])
        total_retx_latency = sum([pkt['Retx Latency'] for pkt in analyzer.all_packets])
        total_latency = total_waiting_latency + total_tx_latency + total_retx_latency
        avg_latency = total_latency / len(analyzer.all_packets)
        variance_latency = sum([(pkt['Waiting Latency'] + pkt['Tx Latency'] + pkt['Retx Latency'] - avg_latency) ** 2 for pkt in analyzer.all_packets]) / len(analyzer.all_packets)

        print(f"Total Latency: {total_latency} ms")
        print(f"Average Latency: {avg_latency} ms")
        print(f"Variance of Latency: {variance_latency} ms^2")
        print(f"Average Waiting Latency: {total_waiting_latency / len(analyzer.all_packets)} ms")
        print(f"Average Transmission Latency: {total_tx_latency / len(analyzer.all_packets)} ms")
        print(f"Average Retransmission Latency: {total_retx_latency / len(analyzer.all_packets)} ms")
    else:
        print("No uplink packet data available for latency analysis.")
