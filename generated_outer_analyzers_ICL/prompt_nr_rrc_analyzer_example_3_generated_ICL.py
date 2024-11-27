
#!/usr/bin/python
# Filename: nr_rrc_analysis_example.py

import os
import sys

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from nr_rrc_analyzer import NrRrcAnalyzer

"""
Example script to process NR RRC messages using NrRrcAnalyzer.
"""

if __name__ == "__main__":

    # Initialize the OfflineReplayer
    src = OfflineReplayer()
    src.set_input_path("./logs/")

    # Enable necessary logs
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    # Initialize the MsgLogger
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./nr_rrc_decoded_messages.txt")
    logger.set_source(src)

    # Initialize the NrRrcAnalyzer
    nr_rrc_analyzer = NrRrcAnalyzer()
    nr_rrc_analyzer.set_source(src)

    # Initialize packet count
    packet_count = 0

    # Define a custom callback to increment and print packet count
    def packet_count_callback(msg):
        nonlocal packet_count
        packet_count += 1
        print(f"Processed packet count: {packet_count}")

    # Add the custom callback to the NrRrcAnalyzer
    nr_rrc_analyzer.add_source_callback(packet_count_callback)

    # Start the analysis
    src.run()
