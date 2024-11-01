
#!/usr/bin/python
# Filename: modified-offline-analysis-filtering.py
import os
import sys

"""
Offline analysis: save the log as a new one with modified filter settings
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer

if __name__ == "__main__":

    # Initialize a 3G/4G monitor
    src = OfflineReplayer()
    src.set_input_path("./offline_log_example.mi2log")

    # Configure the log to be saved with a slightly different set of logs
    src.enable_log("LTE_NAS_ESM_OTA_Incoming_Packet")
    src.enable_log("LTE_RRC_Serv_Cell_Info")
    src.enable_log("LTE_PHY_Connected_Mode_Intra_Freq_Meas")  # New log type for PHY measurements
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("WCDMA_RRC_Serv_Cell_Info")

    # Save log as
    src.save_log_as("./modified_filtered_log.mi2log")

    # Start the monitoring
    src.run()
