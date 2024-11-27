
#!/usr/bin/python
# Filename: ul_mac_latency_analysis.py
import os
import sys

"""
Offline analysis for uplink MAC latency breakdown
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, UlMacLatencyAnalyzer

if __name__ == "__main__":

    try:
        # Initialize a monitor
        src = OfflineReplayer()
        src.set_input_path("./logs/")

        # Enable necessary logs
        src.enable_log("LTE_MAC_UL_Buffer_Status_Internal")
        src.enable_log("5G_NR_RRC_OTA_Packet")
        src.enable_log("LTE_RRC_OTA_Packet")

        # Set up message logger
        logger = MsgLogger()
        logger.set_decode_format(MsgLogger.XML)
        logger.set_dump_type(MsgLogger.FILE_ONLY)
        logger.save_decoded_msg_as("./ul_mac_latency_logs.xml")
        logger.set_source(src)

        # Initialize UlMacLatencyAnalyzer
        ul_mac_latency_analyzer = UlMacLatencyAnalyzer()
        ul_mac_latency_analyzer.set_source(src)

        # Start the monitoring
        src.run()

        # Calculate the average uplink packet latency
        if ul_mac_latency_analyzer.lat_stat:
            total_latency = sum(latency[4] for latency in ul_mac_latency_analyzer.lat_stat)
            average_latency = total_latency / len(ul_mac_latency_analyzer.lat_stat)
            print(f"Average Uplink Latency: {average_latency} ms")
        else:
            print("No latency data collected.")
    
    except Exception as e:
        print(f"An error occurred during the analysis: {e}")
