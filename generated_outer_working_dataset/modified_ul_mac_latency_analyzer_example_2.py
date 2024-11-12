
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py
import os
import sys

"""
Offline analysis by replaying logs
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, UlMacLatencyAnalyzer

if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")
    # src.enable_log_all()

    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./test.txt")
    logger.set_source(src)

    ul_mac_latency_analyzer = UlMacLatencyAnalyzer()
    ul_mac_latency_analyzer.set_source(src)

    # Add a slightly altered calculation or output
    def calculate_average_latency(latencies):
        if not latencies:
            return 0
        total_latency = sum(latency[4] for latency in latencies)
        return total_latency / len(latencies)

    # Start the monitoring
    src.run()

    # After running, calculate and print the average uplink latency
    average_latency = calculate_average_latency(ul_mac_latency_analyzer.lat_stat)
    print(f"Average UL Packet Latency: {average_latency} ms")
