
#!/usr/bin/python
# Filename: modified-offline-analysis-filtering.py
import os
import sys

"""
Modified offline analysis: save the log with updated filter and additional processing
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger

if __name__ == "__main__":

    # Initialize a 3G/4G monitor
    src = OfflineReplayer()
    src.set_input_path("./offline_log_example.mi2log")

    # Configure the log to be saved with an updated filter
    src.enable_log("LTE_NAS_ESM_OTA_Incoming_Packet")
    src.enable_log("LTE_RRC_Serv_Cell_Info")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("WCDMA_RRC_Serv_Cell_Info")
    src.enable_log("WCDMA_RRC_OTA_Packet")
    src.enable_log("5G_NR_RRC_OTA_Packet")  # New log type for 5G NR

    # Set up a logger with a different format and dump type
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.JSON)  # Changed format to JSON
    logger.set_dump_type(MsgLogger.CONSOLE_ONLY)  # Changed dump type to console

    # Bind the logger to the source
    logger.set_source(src)

    # Save log as
    src.save_log_as("./modified_filtered_log.mi2log")

    # Start the monitoring
    src.run()
