
#!/usr/bin/python
# Filename: offline-analysis-modified.py
import os
import sys

"""
Offline analysis: save the log as a new one with a modified filter and additional data processing
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import LteMacAnalyzer

if __name__ == "__main__":

    # Initialize a 3G/4G monitor
    src = OfflineReplayer()
    src.set_input_path("./offline_log_example.mi2log")

    # Configure the log to be saved with additional log types
    src.enable_log("LTE_NAS_ESM_OTA_Incoming_Packet")
    src.enable_log("LTE_RRC_Serv_Cell_Info")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("WCDMA_RRC_Serv_Cell_Info")
    src.enable_log("WCDMA_RRC_OTA_Packet")
    src.enable_log("LTE_MAC_UL_Buffer_Status_Internal")  # New log type

    # Save log as
    src.save_log_as("./modified_filtered_log.mi2log")

    # Initialize an additional analyzer
    mac_analyzer = LteMacAnalyzer()
    mac_analyzer.set_source(src)  # Bind with the monitor

    # Start the monitoring
    src.run()
