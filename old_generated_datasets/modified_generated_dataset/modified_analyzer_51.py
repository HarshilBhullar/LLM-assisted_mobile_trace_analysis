
#!/usr/bin/python
# Filename: offline-analysis-filtering-modified.py
import os
import sys

"""
Offline analysis: save the log as a new one with a modified filter and processing
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger

if __name__ == "__main__":

    # Initialize a 3G/4G monitor
    src = OfflineReplayer()
    src.set_input_path("./offline_log_example.mi2log")

    # Configure the log to be saved with additional logs
    src.enable_log("LTE_NAS_ESM_OTA_Incoming_Packet")
    src.enable_log("LTE_RRC_Serv_Cell_Info")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("WCDMA_RRC_Serv_Cell_Info")
    src.enable_log("WCDMA_RRC_OTA_Packet")
    src.enable_log("5G_NR_RRC_OTA_Packet")  # Added a new log for 5G NR

    # Save log as
    src.save_log_as("./filtered_log_modified.mi2log")

    # Initialize a logger to save decoded messages
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.JSON)  # Changed format to JSON
    logger.set_dump_type(MsgLogger.FILE_AND_STDOUT)  # Output to both file and stdout
    logger.save_decoded_msg_as("./decoded_messages.json")
    logger.set_source(src)

    # Start the monitoring
    src.run()
