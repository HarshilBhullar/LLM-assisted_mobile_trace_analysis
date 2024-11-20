
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py
import os
import sys

"""
Modified offline analysis by replaying logs
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, UlMacLatencyAnalyzer

if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")
    # src.enable_log_all()

    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./modified_test.txt")
    logger.set_source(src)

    ul_mac_latency_analyzer = UlMacLatencyAnalyzer()
    ul_mac_latency_analyzer.set_source(src)

    # Custom modification: Log additional metrics
    def custom_callback(msg):
        if msg.type_id == "LTE_MAC_UL_Buffer_Status_Internal":
            # Assuming we extract some data from the message to log
            # Example: Calculate and log average buffer length over time
            log_item = msg.data.decode()
            buffer_lengths = [int(lcid['Total Bytes']) for subpacket in log_item['Subpackets']
                              for lcid in subpacket.get('LCIDs', [])]
            avg_buffer_length = sum(buffer_lengths) / len(buffer_lengths) if buffer_lengths else 0
            print(f"Average Buffer Length: {avg_buffer_length}")

    ul_mac_latency_analyzer.add_callback(custom_callback)

    # Start the monitoring
    src.run()
