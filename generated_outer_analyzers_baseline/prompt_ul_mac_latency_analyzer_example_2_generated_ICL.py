
#!/usr/bin/python
# Filename: ul_mac_latency_outer_analyzer.py

"""
ul_mac_latency_outer_analyzer.py
Outer analyzer script to perform offline analysis of MAC layer uplink latency using UlMacLatencyAnalyzer

Author: Zhehui Zhang
"""

import sys
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from ul_mac_latency_analyzer import UlMacLatencyAnalyzer

def main(log_path):
    try:
        # Initialize the monitor
        monitor = OfflineReplayer()
        monitor.set_input_path(log_path)

        # Enable necessary logs
        monitor.enable_log("LTE_MAC_UL_Buffer_Status_Internal")
        monitor.enable_log("LTE_RRC_OTA_Packet")
        monitor.enable_log("5G_NR_RRC_OTA_Packet")

        # Initialize the message logger to log decoded messages
        logger = MsgLogger()
        logger.set_decode_format(MsgLogger.XML)
        logger.set_dump_type(MsgLogger.FILE_ONLY)
        logger.save_decoded_msg_as("decoded_messages.xml")
        logger.set_source(monitor)

        # Initialize the UlMacLatencyAnalyzer
        ul_latency_analyzer = UlMacLatencyAnalyzer()
        ul_latency_analyzer.set_source(monitor)

        # Start the monitoring process
        monitor.run()

        # Calculate and print the average uplink latency
        if ul_latency_analyzer.lat_stat:
            total_latency = sum([entry[4] for entry in ul_latency_analyzer.lat_stat])
            average_latency = total_latency / len(ul_latency_analyzer.lat_stat)
            print(f"Average Uplink Packet Latency: {average_latency} ms")
        else:
            print("No uplink latency data collected.")
    
    except Exception as e:
        print(f"An error occurred during the analysis: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ul_mac_latency_outer_analyzer.py <path_to_log_file>")
    else:
        log_file_path = sys.argv[1]
        main(log_file_path)
