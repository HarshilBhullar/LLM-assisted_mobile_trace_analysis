
#!/usr/bin/python
# Filename: ul_mac_latency_analysis.py

import os
import sys

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from ul_mac_latency_analyzer import UlMacLatencyAnalyzer

def print_queue_length(analyzer):
    """
    Callback function to print the current MAC UL buffer queue length.
    """
    print("Current MAC UL buffer queue length:", analyzer.queue_length)

if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")

    # Enable specific logs
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    # Initialize and configure the logger
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./modified_test.txt")
    logger.set_source(src)

    # Integrate the UlMacLatencyAnalyzer
    ul_mac_latency_analyzer = UlMacLatencyAnalyzer()
    ul_mac_latency_analyzer.set_source(src)

    # Define a callback to log queue length
    ul_mac_latency_analyzer.add_source_callback(lambda msg: print_queue_length(ul_mac_latency_analyzer))

    # Start the monitoring and analysis process
    src.run()
