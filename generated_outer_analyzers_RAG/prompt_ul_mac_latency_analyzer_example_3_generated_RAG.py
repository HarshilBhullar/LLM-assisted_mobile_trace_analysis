
#!/usr/bin/python
# Filename: ul_mac_latency_analysis.py
import os
import sys

"""
Offline analysis for uplink MAC layer latency using MobileInsight
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, UlMacLatencyAnalyzer

if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")  # Specify the directory containing log files

    # Enable specific logs
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    # Setup logger
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./modified_test.txt")  # Set the output file for decoded messages
    logger.set_source(src)

    # Setup analyzer
    ul_mac_latency_analyzer = UlMacLatencyAnalyzer()
    ul_mac_latency_analyzer.set_source(src)

    # Custom callback for additional analysis
    total_buffer_length = 0
    buffer_count = 0

    def custom_callback(msg):
        nonlocal total_buffer_length, buffer_count
        if msg.type_id == "LTE_MAC_UL_Buffer_Status_Internal":
            log_item = msg.data.decode()
            if 'Subpackets' in log_item:
                for subpacket in log_item['Subpackets']:
                    if 'Samples' in subpacket:
                        for sample in subpacket['Samples']:
                            if 'LCIDs' in sample:
                                for lcid in sample['LCIDs']:
                                    if 'New Compressed Bytes' in lcid:
                                        total_buffer_length += int(lcid['New Compressed Bytes'])
                                    elif 'New bytes' in lcid:
                                        total_buffer_length += int(lcid['New bytes'])
                                    buffer_count += 1

    ul_mac_latency_analyzer.add_source_callback(custom_callback)

    # Start the monitoring
    src.run()

    # Calculate and print average buffer length
    if buffer_count > 0:
        average_buffer_length = total_buffer_length / buffer_count
        print(f"Average Buffer Length: {average_buffer_length:.2f} bytes")
    else:
        print("No buffer length data available.")
