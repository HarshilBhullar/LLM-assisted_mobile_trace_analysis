
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py
import os
import sys

"""
Modified offline analysis by replaying logs with altered metrics
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, \
    NrRrcAnalyzer

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

    # Analyzers
    nr_rrc_analyzer = NrRrcAnalyzer()
    nr_rrc_analyzer.set_source(src)  # bind with the monitor

    # Additional calculation: log the number of packets processed
    packet_count = 0

    def custom_callback(msg):
        nonlocal packet_count
        packet_count += 1
        print(f"Packet count: {packet_count}")

    nr_rrc_analyzer.add_source_callback(custom_callback)

    src.run()
