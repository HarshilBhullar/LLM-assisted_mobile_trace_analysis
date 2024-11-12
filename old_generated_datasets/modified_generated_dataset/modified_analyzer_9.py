
#!/usr/bin/python
# Filename: offline-analysis-extended.py
import os
import sys

"""
Offline analysis: Enhanced version with additional packet logging and counting
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer

if __name__ == "__main__":

    # Initialize a 3G/4G monitor
    src = OfflineReplayer()
    src.set_input_path("./offline_log_example.mi2log")

    # Configure the log to be saved
    src.enable_log("LTE_NAS_ESM_OTA_Incoming_Packet")
    src.enable_log("LTE_RRC_Serv_Cell_Info")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("WCDMA_RRC_Serv_Cell_Info")
    src.enable_log("WCDMA_RRC_OTA_Packet")
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")  # Additional packet
    src.enable_log("WCDMA_RRC_OTA_Outgoing_Packet")  # Additional packet

    # Initialize packet counters
    packet_count = {
        "LTE_NAS_ESM_OTA_Incoming_Packet": 0,
        "LTE_RRC_Serv_Cell_Info": 0,
        "LTE_RRC_OTA_Packet": 0,
        "WCDMA_RRC_Serv_Cell_Info": 0,
        "WCDMA_RRC_OTA_Packet": 0,
        "LTE_PHY_Serv_Cell_Measurement": 0,
        "WCDMA_RRC_OTA_Outgoing_Packet": 0
    }

    # Define a custom callback to count packet types
    def packet_callback(msg):
        if msg.type_id in packet_count:
            packet_count[msg.type_id] += 1

    # Set the callback function for each message type
    for msg_type in packet_count.keys():
        src.set_callback(msg_type, packet_callback)

    # Save log as
    src.save_log_as("./enhanced_filtered_log.mi2log")

    # Start the monitoring
    src.run()

    # Print packet statistics
    print("Packet Statistics:")
    for packet_type, count in packet_count.items():
        print(f"{packet_type}: {count}")
# ### Key Modifications:
# 1. **Additional Packets**: The analyzer now enables logging of `LTE_PHY_Serv_Cell_Measurement` and `WCDMA_RRC_OTA_Outgoing_Packet`, which were not present in the original code.
# 2. **Packet Counting**: Introduced a packet counting mechanism using a dictionary to keep track of how many times each packet type is processed. This adds a new layer of analysis to the existing functionality.
# 3. **Callback Function**: A custom callback function is defined and set for each packet type to increment the counter whenever a message of that type is processed.
# 4. **Output Statistics**: After the log processing, the script prints out a summary of the packet counts.

# This modified analyzer retains the original structure and style, ensuring consistency with the existing codebase while providing enhanced functionality.