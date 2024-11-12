
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py
import os
import sys

"""
Offline analysis by replaying logs with additional metrics
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, ModemDebugAnalyzer

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
    logger.save_decoded_msg_as("./test_modified.txt")
    logger.set_source(src)

    modem_debug_analyzer = ModemDebugAnalyzer()
    modem_debug_analyzer.set_source(src)

    # Additional functionality: Print a simple metric
    total_messages = 0

    def custom_callback(msg):
        nonlocal total_messages
        if msg.type_id == "Modem_debug_message":
            total_messages += 1

    modem_debug_analyzer.add_source_callback(custom_callback)

    # Start the monitoring
    src.run()

    # Print the metric
    print(f"Total Modem Debug Messages: {total_messages}")
