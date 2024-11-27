
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

    # Additional analysis: Log queue length at each step
    def log_queue_length():
        print("Current MAC UL buffer queue length:", ul_mac_latency_analyzer.queue_length)

    # src.add_callback(log_queue_length)
    # log_queue_length()
    # Start the monitoring
    src.run()

    log_queue_length()
