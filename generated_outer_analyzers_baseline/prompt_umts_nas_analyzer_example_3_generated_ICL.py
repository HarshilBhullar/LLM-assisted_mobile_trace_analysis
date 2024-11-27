
#!/usr/bin/python
# Filename: outer_umts_nas_analyzer.py

"""
An outer analyzer script to utilize UmtsNasAnalyzer for processing UMTS NAS layer events.

Author: Yuanjie Li
Author: Zengwen Yuan
"""

import os
import sys
from mobile_insight.analyzer.analyzer import Analyzer
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from umts_nas_analyzer import UmtsNasAnalyzer  # Ensure this path is correct

def custom_processing(msg):
    """
    Custom processing callback function to handle specific message types.
    """
    if msg.type_id == "UMTS_NAS_MM_State":
        mm_state = msg.data.get("MM State", "")
        print(f"MM State detected: {mm_state}")

def main(log_directory, xml_output_file):
    """
    Main function to set up and run the outer analyzer.
    """
    # Initialize OfflineReplayer
    offline_replayer = OfflineReplayer()
    offline_replayer.set_input_path(log_directory)

    # Enable specific logs for monitoring
    offline_replayer.enable_log("LTE_PHY_Serv_Cell_Measurement")
    offline_replayer.enable_log("5G_NR_RRC_OTA_Packet")
    offline_replayer.enable_log("LTE_RRC_OTA_Packet")
    offline_replayer.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    # Set up MsgLogger
    msg_logger = MsgLogger()
    msg_logger.set_decode_format("xml")
    msg_logger.save_decoded_msg_as(xml_output_file)
    msg_logger.set_source(offline_replayer)

    # Set up UmtsNasAnalyzer
    umts_nas_analyzer = UmtsNasAnalyzer()
    umts_nas_analyzer.set_source(offline_replayer)

    # Set custom processing function for enhanced message handling
    umts_nas_analyzer.add_source_callback(custom_processing)

    # Start replaying and processing logs
    offline_replayer.run()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python outer_umts_nas_analyzer.py <log_directory> <xml_output_file>")
        sys.exit(1)

    log_directory = sys.argv[1]
    xml_output_file = sys.argv[2]

    if not os.path.isdir(log_directory):
        print(f"Error: {log_directory} is not a valid directory.")
        sys.exit(1)

    main(log_directory, xml_output_file)
