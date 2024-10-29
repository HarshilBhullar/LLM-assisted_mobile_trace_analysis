
#!/usr/bin/python
# Filename: offline-analysis-filtering-modified.py
import os
import sys

"""
Modified offline analysis: save the log with additional filters and altered data processing
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer

if __name__ == "__main__":

    # Initialize a 3G/4G monitor
    src = OfflineReplayer()
    src.set_input_path("./offline_log_example.mi2log")

    # Configure the log to be saved with additional filters
    src.enable_log("LTE_NAS_ESM_OTA_Incoming_Packet")
    src.enable_log("LTE_RRC_Serv_Cell_Info")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("WCDMA_RRC_Serv_Cell_Info")
    src.enable_log("WCDMA_RRC_OTA_Packet")
    src.enable_log("WCDMA_L1_Physical_Channel")

    # Apply a different calculation - for example, log only packets with specific criteria
    def filter_packet(packet):
        # Placeholder for packet filtering logic, e.g., only log packets with specific IDs or conditions
        return "SpecificCriteria" in packet.content.decode(errors='ignore')

    src.add_packet_filter(filter_packet)

    # Save log as
    src.save_log_as("./filtered_log_modified.mi2log")

    # Start the monitoring
    src.run()
